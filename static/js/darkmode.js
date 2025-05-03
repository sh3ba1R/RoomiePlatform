// Enhanced Dark Mode Toggle Functionality

document.addEventListener("DOMContentLoaded", function () {
  // Get the toggle button and body element
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // Function to set dark mode
  const enableDarkMode = () => {
    // Add the class to start the transition
    body.classList.add("dark-mode");
    
    // Save preference to localStorage
    localStorage.setItem("darkMode", "enabled");
    
    // Update toggle icon with animation
    updateToggleIcon(true);
    
    // Add subtle animation to page elements
    animatePageElements(true);
  };

  // Function to disable dark mode
  const disableDarkMode = () => {
    // Remove the class to trigger the transition
    body.classList.remove("dark-mode");
    
    // Save preference to localStorage
    localStorage.setItem("darkMode", "disabled");
    
    // Update toggle icon with animation
    updateToggleIcon(false);
    
    // Add subtle animation to page elements
    animatePageElements(false);
  };

  // Function to update toggle icon with smooth animation
  const updateToggleIcon = (isDarkMode) => {
    if (themeToggle) {
      // Add transition class
      themeToggle.classList.add("rotating");
      
      // After a short delay, change the icon
      setTimeout(() => {
        if (isDarkMode) {
          themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
          themeToggle.setAttribute("title", "Switch to Light Mode");
          themeToggle.setAttribute("aria-label", "Switch to Light Mode");
        } else {
          themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
          themeToggle.setAttribute("title", "Switch to Dark Mode");
          themeToggle.setAttribute("aria-label", "Switch to Dark Mode");
        }
        
        // Remove transition class
        setTimeout(() => {
          themeToggle.classList.remove("rotating");
        }, 300);
      }, 150);
    }
  };
  
  // Function to animate page elements when mode changes
  const animatePageElements = (isDarkMode) => {
    // Select important elements to animate
    const cards = document.querySelectorAll('.card');
    const buttons = document.querySelectorAll('.btn-primary, .btn-success');
    const navItems = document.querySelectorAll('.nav-link');
    
    // Add subtle animations with staggered timing
    cards.forEach((card, index) => {
      setTimeout(() => {
        card.classList.add('animate-transition');
        setTimeout(() => {
          card.classList.remove('animate-transition');
        }, 500);
      }, index * 50); // Stagger the animations
    });
    
    // Animate buttons
    buttons.forEach((button, index) => {
      setTimeout(() => {
        button.classList.add('animate-transition');
        setTimeout(() => {
          button.classList.remove('animate-transition');
        }, 500);
      }, index * 30);
    });
    
    // Animate navigation items
    navItems.forEach((item, index) => {
      setTimeout(() => {
        item.classList.add('animate-transition');
        setTimeout(() => {
          item.classList.remove('animate-transition');
        }, 500);
      }, index * 30);
    });
  };

  // Check system preference for dark mode
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  // Check for saved dark mode preference
  const darkMode = localStorage.getItem("darkMode");

  // Apply the saved preference or system preference on load
  if (darkMode === "enabled" || (darkMode === null && prefersDarkScheme.matches)) {
    enableDarkMode();
  } else {
    // Ensure light mode is properly set
    disableDarkMode();
  }

  // Toggle dark mode when the button is clicked
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      // Animate the toggle button
      themeToggle.classList.add("clicked");
      
      setTimeout(() => {
        themeToggle.classList.remove("clicked");
      }, 300);

      // Toggle mode
      const darkMode = localStorage.getItem("darkMode");
      if (darkMode !== "enabled") {
        enableDarkMode();
        // Trigger a custom event that other scripts can listen for
        document.dispatchEvent(new CustomEvent('darkModeChange', { detail: { isDarkMode: true } }));
      } else {
        disableDarkMode();
        // Trigger a custom event that other scripts can listen for
        document.dispatchEvent(new CustomEvent('darkModeChange', { detail: { isDarkMode: false } }));
      }
    });
  }

  // Listen for system preference changes
  prefersDarkScheme.addEventListener("change", (e) => {
    const darkMode = localStorage.getItem("darkMode");
    if (darkMode === null) {
      if (e.matches) {
        enableDarkMode();
        document.dispatchEvent(new CustomEvent('darkModeChange', { detail: { isDarkMode: true } }));
      } else {
        disableDarkMode();
        document.dispatchEvent(new CustomEvent('darkModeChange', { detail: { isDarkMode: false } }));
      }
    }
  });

  // Helper function to detect if a user is on a mobile device
  const isMobileDevice = () => {
    return (window.innerWidth <= 768) || 
           ('ontouchstart' in window) || 
           (navigator.maxTouchPoints > 0);
  };

  // Add special handling for mobile devices
  if (isMobileDevice()) {
    // Make dark mode toggle more prominent on mobile
    if (themeToggle) {
      themeToggle.classList.add('mobile-theme-toggle');
    }
  }
});
