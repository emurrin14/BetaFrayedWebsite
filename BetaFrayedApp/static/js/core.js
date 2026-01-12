document.addEventListener("DOMContentLoaded", () => {
    const hamburgerOpen = document.getElementById("hamburgerOpen");
    const hamburgerClose = document.getElementById("hamburgerClose");
    const menu = document.getElementById("hamburgerMenuContainer");
    const overlay = document.getElementById("hamburgerMenuOverlay");
  
    if (!hamburgerOpen || !menu || !overlay) return;
  
    function openMenu() {
      menu.style.display = "flex";
      overlay.style.display = "block";
  
      hamburgerOpen.classList.add("hamburgerActive");
      hamburgerClose.classList.add("hamburgerCloseActive");
    }
  
    function closeMenu() {
      menu.style.display = "none";
      overlay.style.display = "none";
  
      hamburgerOpen.classList.remove("hamburgerActive");
      hamburgerClose.classList.remove("hamburgerCloseActive");
    }
  
    hamburgerOpen.addEventListener("click", openMenu);
    hamburgerClose.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu);
  });
  