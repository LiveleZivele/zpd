// Check if the dark mode preference is stored in localStorage
const themeToggleButton = document.getElementById('theme-toggle');
const body = document.body;
const currentTheme = localStorage.getItem('theme');

// If dark mode was previously saved, apply it
if (currentTheme === 'dark') {
    body.classList.add('dark-theme');
    themeToggleButton.innerHTML = '<h4>Gaišais režīms</h4>';
} else {
    body.classList.remove('dark-theme');
    themeToggleButton.innerHTML = '<h4>Tumšais režīms</h4>';
}

// Toggle dark/light theme when the button is clicked
themeToggleButton.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    
    // Update the button text based on the current theme
    if (body.classList.contains('dark-theme')) {
        themeToggleButton.innerHTML = '<h4>Gaišais režīms</h4>';
        localStorage.setItem('theme', 'dark'); // Save the dark mode preference
    } else {
        themeToggleButton.innerHTML = '<h4>Tumšais režīms</h4>';
        localStorage.setItem('theme', 'light'); // Save the light mode preference
    }
});