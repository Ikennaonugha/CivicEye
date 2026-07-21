(function () {
  "use strict";

  window.onscroll = function () {
    const ud_header = document.querySelector(".ud-header");
    const logo = document.querySelector(".navbar-brand img");
    const backToTop = document.querySelector(".back-to-top");

    if (ud_header) {
      const sticky = ud_header.offsetTop;

      if (window.pageYOffset > sticky) {
        ud_header.classList.add("sticky");
      } else {
        ud_header.classList.remove("sticky");
      }

      // Guard: Swapping logo source safely if logo element exists
      if (logo) {
        if (ud_header.classList.contains("sticky")) {
          logo.src = logo.src.replace("logo.svg", "logo-2.svg");
        } else {
          logo.src = logo.src.replace("logo-2.svg", "logo.svg");
        }
      }
    }

    // Guard: Only toggle back-to-top button if element exists
    if (backToTop) {
      if (
        document.body.scrollTop > 50 ||
        document.documentElement.scrollTop > 50
      ) {
        backToTop.style.display = "flex";
      } else {
        backToTop.style.display = "none";
      }
    }
  };

  // ===== Close navbar-collapse when a link is clicked & toggle menu
  const navbarToggler = document.querySelector(".navbar-toggler");
  const navbarCollapse = document.querySelector(".navbar-collapse");

  // Guard: Ensure both elements exist before attaching event listeners
  if (navbarToggler && navbarCollapse) {
    document.querySelectorAll(".ud-menu-scroll").forEach((e) =>
      e.addEventListener("click", () => {
        navbarToggler.classList.remove("active");
        navbarCollapse.classList.remove("show");
      })
    );

    navbarToggler.addEventListener("click", function () {
      navbarToggler.classList.toggle("active");
      navbarCollapse.classList.toggle("show");
    });
  }

  // ===== Submenu Handler
  const submenuButton = document.querySelectorAll(".nav-item-has-children");
  submenuButton.forEach((elem) => {
    const anchor = elem.querySelector("a");
    const submenu = elem.querySelector(".ud-submenu");

    // Guard: Ensure anchor and submenu exist within wrapper
    if (anchor && submenu) {
      anchor.addEventListener("click", (e) => {
        e.preventDefault();
        submenu.classList.toggle("show");
      });
    }
  });

  // ===== WOW.js Animation Initializer
  if (typeof WOW === "function") {
    new WOW().init();
  }

  // ====== Scroll To Top Smooth Animation
  function scrollTo(element, to = 0, duration = 500) {
    const start = element.scrollTop;
    const change = to - start;
    const increment = 20;
    let currentTime = 0;

    const animateScroll = () => {
      currentTime += increment;
      const val = Math.easeInOutQuad(currentTime, start, change, duration);
      element.scrollTop = val;

      if (currentTime < duration) {
        setTimeout(animateScroll, increment);
      }
    };

    animateScroll();
  }

  Math.easeInOutQuad = function (t, b, c, d) {
    t /= d / 2;
    if (t < 1) return (c / 2) * t * t + b;
    t--;
    return (-c / 2) * (t * (t - 2) - 1) + b;
  };

  const backToTopBtn = document.querySelector(".back-to-top");
  // Guard: Check button existence before assigning onclick handler
  if (backToTopBtn) {
    backToTopBtn.onclick = () => {
      scrollTo(document.documentElement);
    };
  }
})();