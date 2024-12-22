// loader.js

// Step 1: Create the loader dynamically
const loader = document.createElement('div');
loader.id = 'loader';
loader.innerHTML = `
    <div class="spinner"></div>
    <style>
        #loader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9); /* White background with some transparency */
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid white; /* White borders */
            border-top: 5px solid green; /* Green top border */
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }
    </style>
`;

// Step 2: Add the loader to the DOM immediately
document.body.appendChild(loader);

// Step 3: Remove the loader once the page is fully loaded
window.addEventListener('load', () => {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.opacity = '0'; // Fade out (optional)
        setTimeout(() => loader.remove(), 500); // Remove after fade-out
    }
});
