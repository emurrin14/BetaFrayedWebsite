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



// add to cart logic
// 1. Load the variant data we printed in the HTML
const allVariants = JSON.parse(document.getElementById('variant-data').textContent);
    
// State to track user selection
let selectedColor = null;
let selectedSize = null;

// --- FUNCTION: Handle Color Click ---
function selectColor(colorName, imgElement) {
    selectedColor = colorName;
    selectedSize = null; // Reset size when color changes
    
    // Update UI: Highlight selected image
    document.querySelectorAll('.color-option').forEach(el => el.style.borderColor = 'transparent');
    imgElement.style.borderColor = 'black'; // Or your theme color
    document.getElementById('colorLabel').textContent = colorName
   
    // Filter variants that match this color
    const availableSizes = allVariants
        .filter(v => v.color === colorName)
        .map(v => v.size); // Get just the size names
    
    // Render Size Buttons
    renderSizeButtons(availableSizes);
    updateAddToCartState();
}

// function to render size buttons
const sizeOrder = ["XS", "S", "M", "L", "XL", "XXL"]; // Custom sort order

function renderSizeButtons(sizes) {
    const container = document.getElementById('sizeContainer');
    const template = document.getElementById('size-btn-template'); // Get the blueprint
    
    container.innerHTML = ''; 

    if (sizes.length === 0) {
        container.innerHTML = '<span class="text-gray-500">Out of Stock</span>';
        return;
    }

    // Optional: Sort the sizes based on the array above
    sizes.sort((a, b) => {
        return sizeOrder.indexOf(a) - sizeOrder.indexOf(b);
    });

    sizes.forEach(size => {
        // 1. CLONE the template (true = deep clone)
        const clone = template.content.cloneNode(true);
        
        // 2. FIND the button inside the clone
        const btn = clone.querySelector('button');
        
        // 3. FILL in data
        // If your component has a span with class 'size-text', fill that
        const textSpan = btn.querySelector('.size-text');
        if (textSpan) textSpan.innerText = size;
        else btn.innerText = size; // Fallback if no span
        
        // 4. ATTACH Logic
        btn.onclick = () => {
            // Remove 'active' class from all other buttons
            // (Assumes you have a .active CSS class defined)
            container.querySelectorAll('.size-btn').forEach(b => {
                b.classList.remove('active-size-btn');
                b.style.backgroundColor = ''; 
                b.style.color = '';
            });
            
            // Add 'active' class to clicked button
            btn.classList.add('active-size-btn');
            
            // Your existing logic
            selectedSize = size;
            updateAddToCartState();
        };

        // 5. INJECT into DOM
        container.appendChild(clone);
    });
}

// function to find id and enable button
function updateAddToCartState() {
    const btn = document.getElementById('addToCartBtn');
    const hiddenInput = document.getElementById('selectedVariantId');

    if (selectedColor && selectedSize) {
        // find the exact variant id
        const variant = allVariants.find(v => v.color === selectedColor && v.size === selectedSize);
            
        if (variant) {
            hiddenInput.value = variant.id;
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.innerText = "Add to Cart - " + selectedSize;
        }
    } else {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    }
}

// function to send to view
function submitToCart() {
    const form = document.getElementById('addToCartForm');
    
    // get the id from the html data attribute
    const productId = form.getAttribute('data-product-id'); 

    const formData = new FormData(form);


//fetch url and send json data
    fetch(`/add-to-cart/${productId}/`, { 
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("Added to cart! Total items: " + data.quantity);
        } else {
            alert("Error adding to cart.");
        }
    })
    .catch(err => console.error('Error:', err));
}

document.addEventListener("DOMContentLoaded", () => {
    const firstColorImg = document.querySelector(".color-option");

    if (firstColorImg) {
        const colorName = firstColorImg.getAttribute("data-color");
        selectColor(colorName, firstColorImg);
    }
});