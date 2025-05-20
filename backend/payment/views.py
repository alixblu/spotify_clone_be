from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from bson import ObjectId
from .models import Payment
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import paypalrestsdk

from user_management.models import User




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
        
        user_id = ObjectId(user_id) if user_id else None
        
        if not amount:
            return JsonResponse({"error": "Amount is required"}, status=400)

        # Get user if user_id is provided
        user = None
        if user_id:
            try:
                # Use id field for User model
                user = User.objects.get(_id=user_id)
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
                    "total": amount,
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
                amount=amount,
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
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        paypal_payment = paypalrestsdk.Payment.find(payment_id)

        if paypal_payment.execute({"payer_id": payer_id}):
            payment.status = 'completed'
            payment.save()
            return redirect('/payment/success/')
        else:
            payment.status = 'failed'
            payment.save()
            return redirect('/payment/failed/')
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@csrf_exempt
@require_POST
def ipn_listener(request):
    """Handle PayPal IPN notifications"""
    try:
        # Verify IPN message
        if not paypalrestsdk.notification.webhook_event.verify(request.body):
            return HttpResponse("Invalid IPN", status=400)

        # Parse IPN data
        ipn_data = json.loads(request.body)
        
        # Find payment by transaction ID
        payment = Payment.objects.get(payment_id=ipn_data.get('txn_id'))
        
        # Update payment status based on IPN
        if ipn_data.get('payment_status') == 'Completed':
            payment.status = 'completed'
        elif ipn_data.get('payment_status') == 'Refunded':
            payment.status = 'refunded'
        elif ipn_data.get('payment_status') == 'Failed':
            payment.status = 'failed'
            
        # Store IPN data
        payment.ipn_data = ipn_data
        payment.save()
        
        return HttpResponse("IPN processed", status=200)
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@login_required
def cancel_payment(request):
    """Handle payment cancellation"""
    payment_id = request.GET.get('paymentId')
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        payment.status = 'failed'
        payment.save()
        return redirect('/payment/cancelled/')
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)