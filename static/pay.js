
        $(document).ready(function() {
            $("#payment-form").submit(function(e) {
                e.preventDefault(); // Prevent default form submission

                var name = $("#payment-form input[name='name']").val();
                var phone = $("#payment-form input[name='phone']").val();
                var email = $("#payment-form input[name='email']").val();
                var amount = $("#payment-form input[name='amount']").val();

                if (name != "" && phone != "" && email != "" && amount != "") {
                    // Replace 'YOUR_API_KEY' with your actual Razorpay API key
                    var options = {
                        key: "rzp_test_yEEyHCtwXFZUIR",
                        name: "Ticket Pranali",
                        description: "Ticket",
                        image: "logo.jpg",
                        prefill: {
                            name: name,
                            email: email,
                            contact: phone
                        },
                        theme: {
                            color: "#fea317"
                        },
                        amount: amount * 100,
                        currency: "INR",
                        handler: function(response) {
                            // Handle successful payment here
                            console.log("Payment successful:", response);
                            // Redirect to a success page or display a confirmation message
                        },
                        modal: {
                            ondismiss: function() {
                                console.log("Modal closed");
                            }
                        }
                    };

                    var rzp1 = new Razorpay(options);
                    rzp1.on('payment.failed', function(response) {
                        console.log("Payment Failed!");
                    });
                    rzp1.open();
                } else {
                    alert("Please fill in all required fields.");
                }
            });
        });
    
