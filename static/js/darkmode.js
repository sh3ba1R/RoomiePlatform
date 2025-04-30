// Enhanced Dark Mode Toggle Functionality

document.addEventListener("DOMContentLoaded", function () {
  // Get the toggle button and body element
  const darkModeToggle = document.getElementById("darkModeToggle");
  const body = document.body;

  // Function to set dark mode
  const enableDarkMode = () => {
    // Add the class to start the transition
    body.classList.add("dark-mode");

    // Save preference to localStorage
    localStorage.setItem("darkMode", "enabled");

    // Update toggle icon with animation
    updateToggleIcon(true);
  };

  // Function to disable dark mode
  const disableDarkMode = () => {
    // Remove the class to trigger the transition
    body.classList.remove("dark-mode");

    // Save preference to localStorage
    localStorage.setItem("darkMode", "disabled");

    // Update toggle icon with animation
    updateToggleIcon(false);
  };

  // Function to update toggle icon with smooth animation
  const updateToggleIcon = (isDarkMode) => {
    if (darkModeToggle) {
      // Add transition class
      darkModeToggle.classList.add("rotating");

      // After a short delay, change the icon
      setTimeout(() => {
        if (isDarkMode) {
          darkModeToggle.innerHTML =
            '<i class="fas fa-sun dark-mode-icon"></i>';
          darkModeToggle.setAttribute("title", "Switch to Light Mode");
        } else {
          darkModeToggle.innerHTML =
            '<i class="fas fa-moon dark-mode-icon"></i>';
          darkModeToggle.setAttribute("title", "Switch to Dark Mode");
        }

        // Remove transition class
        setTimeout(() => {
          darkModeToggle.classList.remove("rotating");
        }, 200);
      }, 150);
    }
  };

  // Check system preference for dark mode
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  // Check for saved dark mode preference
  const darkMode = localStorage.getItem("darkMode");

  // Apply the saved preference or system preference on load
  if (
    darkMode === "enabled" ||
    (darkMode === null && prefersDarkScheme.matches)
  ) {
    enableDarkMode();
  }

  // Toggle dark mode when the button is clicked
  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", () => {
      // Animate the toggle button
      darkModeToggle.classList.add("clicked");
      setTimeout(() => {
        darkModeToggle.classList.remove("clicked");
      }, 300);

      // Toggle mode
      const darkMode = localStorage.getItem("darkMode");
      if (darkMode !== "enabled") {
        enableDarkMode();
      } else {
        disableDarkMode();
      }
    });
  }

  // Listen for system preference changes
  prefersDarkScheme.addEventListener("change", (e) => {
    const darkMode = localStorage.getItem("darkMode");
    if (darkMode === null) {
      if (e.matches) {
        enableDarkMode();
      } else {
        disableDarkMode();
      }
    }
  });
});
