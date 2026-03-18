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
    const emailFormText = document.getElementById('form-text');
    const emailForm = document.getElementById('email-form');
    const responseDiv = document.getElementById('form-response');
    const submitBtn = document.getElementById('email-submit-button');
    const ThanksText = document.querySelector('.main-form-container-subscribed');

    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Visual feedback
            submitBtn.innerText = 'Signing up...';
            submitBtn.disabled = true;
            responseDiv.style.display = 'none'; // hide previous messages on new submit

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
                    if (data.status === 'success') {
                        // Hide form and Show Thanks Text
                        emailFormText.style.display = 'none';
                        emailForm.style.display = 'none';
                        ThanksText.style.display = 'flex';
                        emailForm.reset(); 
                    } else if (data.status === 'exists') {
                        // Keep form visible, show 'already subscribed' message
                        responseDiv.textContent = data.message;
                        responseDiv.style.color = "orange"; // You can change this to any color
                        responseDiv.style.display = 'block';
                    }
                } else {
                    responseDiv.textContent = data.message || "Error occurred.";
                    responseDiv.style.color = "red";
                    responseDiv.style.display = 'block';
                }
            } catch (error) {
                responseDiv.textContent = "Connection error.";
                responseDiv.style.color = "red";
                responseDiv.style.display = 'block';
            } finally {
                submitBtn.innerText = 'Sign Up';
                submitBtn.disabled = false;
            }
        });
    }
});