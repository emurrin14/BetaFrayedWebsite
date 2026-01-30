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




// update ajax cart quantity
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.update-cart-btn');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.item;
            const action = this.dataset.action;
            
            updateCart(itemId, action);
        });
    });
});

function updateCart(itemId, action) {
    const url = "{% url 'update_cart_item' %}";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}', // Django requires this
        },
        body: JSON.stringify({
            'item_id': itemId,
            'action': action
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.removed) {
            // If quantity is 0, remove the row
            document.getElementById(`item-row-${itemId}`).remove();
        } else {
            // Update Quantity
            document.getElementById(`qty-${itemId}`).innerText = data.quantity;
            // Update Item Subtotal
            document.getElementById(`subtotal-${itemId}`).innerText = "$" + data.item_subtotal;
        }
        
        // Update Cart Grand Total
        document.getElementById('cart-total-price').innerText = "$" + data.cart_total + " USD";
        
        // Optional: Update top header count (e.g. "Your Cart (3 items)")
        const header = document.querySelector('.yourCart');
        if(header) {
            header.innerText = `Your Cart (${data.total_items} items):`;
        }
    });
}