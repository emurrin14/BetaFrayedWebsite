// logic for fetching the stripe url with create_checkout_session view through a post request
document.addEventListener("DOMContentLoaded", function () {
  const checkoutButton = document.getElementById("checkout-button");
  if (!checkoutButton) return;

  // reset button state on reload script
  checkoutButton.disabled = false;
  checkoutButton.querySelector(".checkout-text").textContent = "Checkout";
  checkoutButton.classList.remove("checkout-button-processing");

  checkoutButton.addEventListener("click", function (event) {
      event.preventDefault();

      //disable button
      checkoutButton.disabled = true;
      checkoutButton.querySelector(".checkout-text").textContent = "Processing..";
      checkoutButton.classList.add("checkout-button-processing");

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch("/create-checkout-session/", {
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
      })
          .then(r => r.json())
          .then(data => {
              if (data.error) {
                  alert("Error: " + data.error);

                  // RE-ENABLE ON SERVER ERROR
                  checkoutButton.disabled = false;
                  checkoutButton.textContent = "Checkout";
                  checkoutButton.classList.remove("checkout-button-processing");

                  return;
              }

              const stripe = Stripe(window.stripePublicKey);
              stripe.redirectToCheckout({ sessionId: data.id });
          })
          .catch(err => {
              console.error("Checkout error:", err);

              // RE-ENABLE ON NETWORK ERROR
              checkoutButton.disabled = false;
              checkoutButton.textContent = "Checkout";
              checkoutButton.classList.remove("checkout-button-processing");
          });
  });
});