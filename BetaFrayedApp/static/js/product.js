// clickable image thumbnails
document.addEventListener("DOMContentLoaded", () => {
    const mainImg = document.getElementById("heroImage");
    const thumbnails = document.querySelectorAll(".thumbnail");
  
    if (!mainImg || thumbnails.length === 0) return;
  
    thumbnails.forEach((thumb) => {
      thumb.addEventListener("click", () => {
        mainImg.src = thumb.src;

        thumbnails.forEach((t) =>
          t.classList.remove("thumbnail-active")
        );
        thumb.classList.add("thumbnail-active");
      });
    });
  });


  document.addEventListener('DOMContentLoaded', function() {
    
    // --- PART 1: SETUP & VARIABLES ---
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    const productContainer = document.querySelector('.product-container');
    const variantDataScript = document.getElementById('variant-data');

    // Safety check: If we aren't on a product page, stop running
    if (!addToCartBtn || !variantDataScript) return;

    // Parse the JSON data ONCE so we can use it everywhere
    const variants = JSON.parse(variantDataScript.textContent);

    const colorInputs = document.querySelectorAll('input[name="color"]');
    const sizeWrapper = document.getElementById('size-wrapper');
    const sizeOptions = sizeWrapper.querySelectorAll('.variant-option'); 
    const messageDiv = document.getElementById('cart-message');


    // --- PART 2: UI LOGIC (DEPENDENT OPTIONS) ---
        function toggleButtonState() {
            const colorSelected = document.querySelector('input[name="color"]:checked');
            const sizeSelected = document.querySelector('input[name="size"]:checked');
        
            if (colorSelected && sizeSelected) {
                addToCartBtn.classList.add('active-add-to-cart-btn');
                messageDiv.innerText = "";
            } else {
                addToCartBtn.classList.remove('active-add-to-cart-btn');
            }
        }
        

    
        function updateSizeAvailability(selectedColor) {
        // 1. Find all variants for this color
        const colorVariants = variants.filter(v => v.color === selectedColor);

        // 2. Create a map of sizes to their stock status
        // Example: { "S": 5, "M": 0, "L": 10 }
        const sizeStockMap = {};
        colorVariants.forEach(v => {
            sizeStockMap[v.size] = v.stock;
        });

        // 3. Loop through all buttons and update state
        sizeOptions.forEach(optionLabel => {
            const sizeInput = optionLabel.querySelector('input');
            const sizeName = sizeInput.value;
            const stockCount = sizeStockMap[sizeName];

            // Reset classes
            sizeInput.checked = false;
            optionLabel.classList.remove('unavailable', 'out-of-stock');
            sizeInput.disabled = false;

            if (stockCount === undefined) {
                // stock quantity doesnt exist
                optionLabel.classList.add('unavailable');
                sizeInput.disabled = true;
                if (sizeInput.checked) sizeInput.checked = false;

            } else if (stockCount === 0) {
                // stock is 0
                optionLabel.classList.add('out-of-stock');
                sizeInput.disabled = true;
                if (sizeInput.checked) sizeInput.checked = false;

            } 
            
        });
        // after unchecking everything, update button state
        toggleButtonState();
    }

    // Listen for Color changes
    colorInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateSizeAvailability(this.value);
            messageDiv.innerText = "";
        });
    });

    // Listen for size changes
    const sizeInputs = document.querySelectorAll('input[name="size"]');
    sizeInputs.forEach(input => {
        input.addEventListener('change', function() {
            toggleButtonState();
        });
    });

    // Run once on load (in case browser remembered a selection on refresh)
    const preSelectedColor = document.querySelector('input[name="color"]:checked');
    if (preSelectedColor) {
        updateSizeAvailability(preSelectedColor.value);
    }


    // --- PART 3: ADD TO CART LOGIC ---

    addToCartBtn.addEventListener('click', function() {
        const productId = productContainer.dataset.productId;
        
        // Get Selected Values
        const sizeInput = document.querySelector('input[name="size"]:checked');
        const colorInput = document.querySelector('input[name="color"]:checked');
        const quantity = document.getElementById('quantity-input').value;

        // Reset message
        messageDiv.innerText = "";
        messageDiv.style.color = "black";

        // Validate Selection
        if (!this.classList.contains('active-add-to-cart-btn')) {
            messageDiv.innerText = "Please select a size and color.";
            messageDiv.style.color = "red";
            return;
        }
        if (!colorInput) {
            messageDiv.innerText = "Please select a color.";
            messageDiv.style.color = "red";
            return;
        }
        if (!sizeInput) {
            messageDiv.innerText = "Please select a size.";
            messageDiv.style.color = "red";
            return;
        }
        
        
        const qty = parseInt(quantity);
        const size = sizeInput.value;
        const color = colorInput.value;

        // Find Matching Variant ID
        const selectedVariant = variants.find(v => v.size === size && v.color === color);

        if (!selectedVariant) {
            messageDiv.innerText = "This combination is currently unavailable.";
            messageDiv.style.color = "red";
            return;
        }
        // Quantity Checks
        if (isNaN(qty) || qty <= 0) {
            messageDiv.innerText = "Please enter a valid quantity.";
            messageDiv.style.color = "red";
            return;
        }
        if (qty > selectedVariant.stock) {
            messageDiv.innerText = 'Quantity is more than item stock.';
            messageDiv.style.color = "red";
            return;
        }

        // Send to Django
        const formData = new FormData();
        formData.append('variant_id', selectedVariant.id);
        formData.append('quantity', quantity);

        fetch(`/add-to-cart/${productId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.innerText = "Added to Cart!";
                messageDiv.style.color = "green";
            } else {
                messageDiv.innerText = "Error adding to cart.";
                messageDiv.style.color = "red";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.innerText = "Server Error.";
            messageDiv.style.color = "red";
        });
    });
});

// Helper for CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}