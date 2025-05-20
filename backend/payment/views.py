from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from bson import ObjectId
from .models import Payment
from django.shortcuts import redirect
import paypalrestsdk

from user_management.models import User
from .models import Payment

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@csrf_exempt
def create_payment(request):
    """Create a PayPal payment"""
    try:
        # Get the amount and user_id from the request body (JSON)
        data = json.loads(request.body)
        amount = data.get('amount')
        user_id = data.get('user_id')
        
        if not amount:
            return JsonResponse({"error": "Amount is required"}, status=400)
        print(f"Received amount: {amount}")  # Debugging line
        print(type(amount))  # Debugging line

        try:
            # Convert amount to Decimal, handling both string and numeric inputs
            amount_decimal = Decimal(str(amount))  # Convert to string first, then to Decimal
            if amount_decimal <= 0:
                return JsonResponse({"error": "Amount must be greater than 0"}, status=400)
        except (InvalidOperation, TypeError, ValueError) as e:
            return JsonResponse({"error": f"Invalid amount format: {str(e)}"}, status=400)

        print(type(amount_decimal))  # Debugging line
        # Get user if user_id is provided
        user = None
        if user_id:
            try:
                user = User.objects.get(_id=ObjectId(user_id))
            except User.DoesNotExist:
                print(f"User not found with id: {user_id}")
                pass
            except Exception as e:
                print(f"Error finding user: {str(e)}")
                pass

        # Create the payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{settings.BASE_URL}/payment/execute/",
                "cancel_url": f"{settings.BASE_URL}/payment/cancel/"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount_decimal.quantize(Decimal("0.01"))),
                    "currency": "USD"
                },
                "description": "Premium Subscription"
            }]
        })

        if payment.create():
            # Store payment in database
            Payment.objects.create(
                user=user,
                payment_id=payment.id,
                amount=amount_decimal,  # Store as Decimal
                status='pending'
            )
            # Find the approval URL in the payment links
            for link in payment.links:
                if link.rel == "approval_url":
                    return JsonResponse({
                        'redirect_url': link.href
                    })
            return JsonResponse({"error": "No approval URL found"}, status=400)
        else:
            print("PayPal Error:", payment.error)  # Add error logging
            return JsonResponse({"error": f"Payment creation failed: {payment.error}"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print("Error creating payment:", str(e))  # Add error logging
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def execute_payment(request):
    """Execute a PayPal payment after user approval"""
    payment_id = request.GET.get('paymentId')     # This is a PayPal string ID
    payer_id = request.GET.get('PayerID')         # Also a string, NOT ObjectId
    token = request.GET.get('token')              # Get the token as well

    print(f"Executing payment - PaymentID: {payment_id}, PayerID: {payer_id}, Token: {token}")  # Debug log

    if not payment_id or not payer_id:
        return JsonResponse({'error': 'Missing paymentId or PayerID'}, status=400)

    try:
        # Find local payment record by PayPal string payment_id
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            print(f"Found payment record: {payment}")  # Debug log
        except Payment.DoesNotExist:
            print(f"Payment not found in database: {payment_id}")  # Debug log
            return HttpResponse("Payment not found", status=404)

        # Execute the payment via PayPal SDK
        try:
            paypal_payment = paypalrestsdk.Payment.find(payment_id)
            print(f"Found PayPal payment: {paypal_payment}")  # Debug log
            
            # Execute the payment with just the payer_id
            if paypal_payment.execute({"payer_id": payer_id}):
                print("Payment executed successfully")  # Debug log

                # Extract amount string safely from PayPal response
                try:
                    amount_str = paypal_payment['transactions'][0]['amount']['total']
                    amount_decimal = Decimal(amount_str)  # Ensure it's a valid Decimal
                except Exception as e:
                    print(f"Error parsing amount from PayPal response: {str(e)}")
                    amount_decimal = None

                # Update payment record
                payment.status = 'completed'
                if amount_decimal:
                    payment.amount = amount_decimal
                payment.save()

                # Update user's premium status if payment is successful
                if payment.user:
                    try:
                        from user_management.services import activate_premium
                        result = activate_premium(payment.user.email)
                        print(f"Premium activation result: {result}")  # Debug log
                    except Exception as e:
                        print(f"Error activating premium: {str(e)}")  # Debug log

                return redirect('/payment/success/')
            else:
                print(f"Payment execution failed: {paypal_payment.error}")  # Debug log
                payment.status = 'failed'
                payment.save()
                return redirect('/payment/failed/')
        except Exception as e:
            print(f"Error executing PayPal payment: {str(e)}")  # Debug log
            payment.status = 'failed'
            payment.save()
            return redirect('/payment/failed/')
            
    except Exception as e:
        print(f"Unexpected error in execute_payment: {str(e)}")  # Debug log
        return HttpResponse(f"Error: {str(e)}", status=500)


@csrf_exempt
def cancel_payment(request):
    """Handle payment cancellation"""
    payment_id = request.GET.get('paymentId')
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        payment.status = 'cancelled'
        payment.save()
        return redirect('/payment/cancelled/')
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
    except Exception as e:
        print("Error cancelling payment:", str(e))  # Add error logging
        return HttpResponse(f"Error: {str(e)}", status=500)

@csrf_exempt
@require_POST
def ipn_listener(request):
    """Handle PayPal IPN notifications"""
    try:
        # Log the raw request data
        print("=== IPN Request Details ===")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        
        # Get the raw POST data
        raw_data = request.body.decode('utf-8')
        
        # Add cmd=_notify-validate to the beginning of the data
        verify_data = 'cmd=_notify-validate&' + raw_data
        
        # Send verification request to PayPal
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Python-IPN-VerificationScript'
        }
        
        # Use sandbox URL for testing, live URL for production
        verify_url = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr' if settings.PAYPAL_MODE == 'sandbox' else 'https://ipnpb.paypal.com/cgi-bin/webscr'
        
        import requests
        response = requests.post(verify_url, data=verify_data, headers=headers)
        
        if response.text != 'VERIFIED':
            print("IPN verification failed")
            return HttpResponse("Invalid IPN", status=400)

        # Parse IPN data
        try:
            ipn_data = dict(item.split("=") for item in raw_data.split("&"))
        except Exception as e:
            print(f"Error parsing IPN data: {str(e)}")
            return HttpResponse("Invalid IPN data format", status=400)
        
        # Get transaction ID from either txn_id or parent_txn_id
        transaction_id = ipn_data.get('txn_id') or ipn_data.get('parent_txn_id')
        if not transaction_id:
            print("No transaction ID found in IPN data")
            return HttpResponse("No transaction ID", status=400)
            
        # Find payment by transaction ID
        try:
            payment = Payment.objects.get(payment_id=transaction_id)
            
            # Only process if payment status has changed
            payment_status = ipn_data.get('payment_status')
            if payment_status != payment.status:
                print(f"Updating payment status from {payment.status} to {payment_status}")
                
                if payment_status == 'Completed':
                    payment.status = 'completed'
                    # Update user's premium status if payment is successful
                    if payment.user:
                        try:
                            from user_management.services import activate_premium
                            result = activate_premium(payment.user.email)
                            print(f"Premium activation result: {result}")
                        except Exception as e:
                            print(f"Error activating premium: {str(e)}")
                elif payment_status == 'Refunded':
                    payment.status = 'refunded'
                elif payment_status == 'Failed':
                    payment.status = 'failed'
                    
                # Store IPN data
                payment.ipn_data = ipn_data
                payment.save()
                print(f"Payment {transaction_id} updated to {payment_status}")
            else:
                print(f"Payment {transaction_id} already in {payment_status} state - skipping update")
            
            return HttpResponse("IPN processed", status=200)
        except Payment.DoesNotExist:
            print(f"Payment not found for IPN txn_id: {transaction_id}")
            return HttpResponse("Payment not found", status=404)
            
    except Exception as e:
        print(f"Error processing IPN: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

def payment_success(request):
    """Handle successful payment"""
    html = f"""
    <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
        <h1 style="color: #28a745;">Payment Successful!</h1>
        <p style="font-size: 18px; margin: 20px 0;">Thank you for your payment. Your premium subscription has been activated.</p>
        <a href="{settings.FRONTEND_URL}/home" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">Return to Home</a>
    </div>
    """
    return HttpResponse(html)

def payment_failed(request):
    """Handle failed payment"""
    html = f"""
    <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
        <h1 style="color: #dc3545;">Payment Failed</h1>
        <p style="font-size: 18px; margin: 20px 0;">We're sorry, but your payment could not be processed. Please try again.</p>
        <a href="{settings.FRONTEND_URL}/home" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">Return to Home</a>
    </div>
    """
    return HttpResponse(html)

def payment_cancelled(request):
    """Handle cancelled payment"""
    html = f"""
    <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
        <h1 style="color: #ffc107;">Payment Cancelled</h1>
        <p style="font-size: 18px; margin: 20px 0;">Your payment was cancelled. You can try again whenever you're ready.</p>
        <a href="{settings.FRONTEND_URL}/home" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">Return to Home</a>
    </div>
    """
    return HttpResponse(html)