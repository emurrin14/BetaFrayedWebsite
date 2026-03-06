document.addEventListener('DOMContentLoaded', () => {
    // --- 1. TOGGLE LOCK/PASSWORD FORM ---
    const lockLink = document.querySelector('.lock-img-link');
    const passwordContainer = document.getElementById('password-form-container');

    if (lockLink && passwordContainer) {
        lockLink.addEventListener('click', (e) => {
            e.preventDefault();        
            passwordContainer.classList.toggle('active');

            if (passwordContainer.classList.contains('active')) {
                passwordContainer.querySelector('input').focus();
            }
        });
    }

    // --- 2. ASYNC EMAIL SUBMISSION ---
    const emailForm = document.getElementById('email-form');
    const responseDiv = document.getElementById('form-response');
    const submitBtn = document.getElementById('email-submit-button');

    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Visual feedback
            submitBtn.innerText = 'Signing up...';
            submitBtn.disabled = true;

            const formData = new FormData(this);

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    responseDiv.textContent = "Thanks For Subscribing!";
                    responseDiv.style.color = "black";
                    emailForm.reset(); 
                } else {
                    responseDiv.textContent = data.message || "Error occurred.";
                    responseDiv.style.color = "red";
                }
            } catch (error) {
                responseDiv.textContent = "Connection error.";
                responseDiv.style.color = "red";
            } finally {
                responseDiv.style.display = 'block';
                submitBtn.innerText = 'Sign Up';
                submitBtn.disabled = false;
            }
        });
    }
});