// tumsais rezims
const themeToggleButton = document.getElementById('theme-toggle');
const body = document.body;
const currentTheme = localStorage.getItem('theme');


if (currentTheme === 'dark') {
    body.classList.add('dark-theme');
    themeToggleButton.innerHTML = '<h4>Gaišais režīms</h4>';
} else {
    body.classList.remove('dark-theme');
    themeToggleButton.innerHTML = '<h4>Tumšais režīms</h4>';
}


themeToggleButton.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    
   
    if (body.classList.contains('dark-theme')) {
        themeToggleButton.innerHTML = '<h4>Gaišais režīms</h4>';
        localStorage.setItem('theme', 'dark'); 
    } else {
        themeToggleButton.innerHTML = '<h4>Tumšais režīms</h4>';
        localStorage.setItem('theme', 'light'); 
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const heartButtons = document.querySelectorAll(".heart-button");

    heartButtons.forEach(button => {
      button.addEventListener("click", function() {
        const bookId = this.getAttribute("data-book-id");

        fetch('/add_to_wishlist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ book_id: bookId }),
        })
        .then(response => {
          if (response.ok) {
            alert("Book added to wishlist!");
            window.location.href = "/veloslasit"; 
          } else {
            alert("Failed to add book to wishlist.");
          }
        });
      });
    });
  });
  fetch('/add_to_wishlist', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ book_id: bookId }),
})
.then(response => response.json())
.then(data => {
    if (data.message === 'Book added to wishlist' || data.message === 'Book removed from wishlist') {
       
        this.style.color = this.style.color === 'green' ? 'red' : 'green';
        alert(data.message); 

      
        window.location.href = '/wishlist'; 
    } else {
        alert("An error occurred: " + data.error);
    }
})
.catch(error => {
    alert("Failed to update wishlist: " + error);
});