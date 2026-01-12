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