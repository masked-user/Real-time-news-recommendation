// Utility function to render articles
function renderArticles(articles, skipInvalidArticles = true) {
    let carouselItems = '';
    let rightCardContent = '';
    let bottomCards = '';
    let count = 0;

    for (let item of articles) {
        // Validate article data
        const isValidArticle = (skipInvalidArticles) 
            ? (item.urlToImage || item.articleImage) && 
              (item.title || item.articleTitle) && 
              item.description && 
              (item.url || item.articleUrl)
            : true; 

        if (!isValidArticle) continue;

        const articleData = {
            image: item.urlToImage || item.articleImage,
            title: item.title || item.articleTitle,
            description: item.description,
            url: item.url || item.articleUrl
        };

        if (!articleData.image || !articleData.title || !articleData.url) continue;

        if (count < 3) {
            // Populate the carousel for the first 3 articles
            carouselItems += `
                <a href="${articleData.url}" target="_blank" class="text-decoration-none">
                    <div class="carousel-item ${count === 0 ? 'active' : ''}">
                        <img src="${articleData.image}" class="d-block w-100" alt="${articleData.title}">
                        <div class="carousel-caption d-none d-md-block">
                            <h5>${articleData.title}</h5>
                        </div>
                    </div>
                </a>
            `;
        } else if (count === 3) {
            // Populate the right-side card for the 4th article
            rightCardContent = `
                <img src="${articleData.image}" class="card-img-top" alt="${articleData.title}">
                <div class="card-body">
                    <h5 class="card-title">${articleData.title}</h5>
                    <p class="card-text">${articleData.description}</p>
                    <a href="${articleData.url}" target="_blank" class="btn btn-primary"
                    data-title="${encodeURIComponent(articleData.title)}" 
                    data-url="${encodeURIComponent(articleData.url)}" 
                    data-description="${encodeURIComponent(articleData.description)}">
                    Read More..</a>
                </div>
            `;
        } else {
            // Populate the bottom cards for the remaining articles
            bottomCards += `
                <div class="col-md-3 mb-3">
                    <div class="card h-100">
                        <img src="${articleData.image}" class="card-img-top" alt="${articleData.title}">
                        <div class="card-body">
                            <h5 class="card-title">${articleData.title}</h5>
                            <p class="card-text">${articleData.description}</p>
                            <a href="${articleData.url}" target="_blank" class="btn btn-primary read-more"
                            data-title="${encodeURIComponent(articleData.title)}" 
                            data-url="${encodeURIComponent(articleData.url)}" 
                            data-description="${encodeURIComponent(articleData.description)}">
                            Read More..</a>
                        </div>
                    </div>
                </div>
            `;
        }
        count++;
    }

    // Update DOM
    document.querySelector(".carousel-inner").innerHTML = carouselItems;
    document.querySelector(".content-right").innerHTML = rightCardContent;
    document.querySelector(".content").innerHTML = bottomCards;
}

// Modern Pagination Class
class Pagination {
    constructor(config = {}) {
        this.totalPages = config.totalPages || 15;
        this.visiblePages = config.visiblePages || 3;
        this.containerId = config.containerId || 'pagination';
        this.activePage = config.activePage || 'home';
        this.currentPage = 1;
        this.currentWindow = 1;
        this.container = document.getElementById(this.containerId);

        this.init();
    }

    init() {
        this.render();
        fetchNews(this.currentPage, this.activePage);
    }

    changeActivePage(newActivePage) {
        this.currentPage = 1;
        this.currentWindow = 1;
        this.activePage = newActivePage;
        this.render();
        fetchNews(this.currentPage, this.activePage);
    }

    render() {
        this.container.innerHTML = '';
        const windowStart = (this.currentWindow - 1) * this.visiblePages + 1;
        const windowEnd = Math.min(windowStart + this.visiblePages - 1, this.totalPages);

        if (this.currentWindow > 1) {
            this.container.appendChild(this.createPageItem('&laquo;', () => this.changePage('prev-window')));
        }

        for (let i = windowStart; i <= windowEnd; i++) {
            const pageItem = this.createPageItem(i, () => this.goToPage(i));
            if (i === this.currentPage) {
                pageItem.querySelector('a').classList.add('active');
            }
            this.container.appendChild(pageItem);
        }

        if (this.currentWindow < Math.ceil(this.totalPages / this.visiblePages)) {
            this.container.appendChild(this.createPageItem('&raquo;', () => this.changePage('next-window')));
        }
    }

    createPageItem(text, clickHandler) {
        const li = document.createElement('li');
        li.classList.add('page-item');

        const a = document.createElement('a');
        a.classList.add('page-link');
        a.innerHTML = text;
        a.href = '#';
        a.addEventListener('click', (e) => {
            e.preventDefault();
            clickHandler();
        });

        li.appendChild(a);
        return li;
    }

    changePage(action) {
        switch(action) {
            case 'prev-window':
                this.currentWindow = Math.max(1, this.currentWindow - 1);
                this.currentPage = (this.currentWindow - 1) * this.visiblePages + 1;
                break;
            case 'next-window':
                this.currentWindow = Math.min(
                    Math.ceil(this.totalPages / this.visiblePages),
                    this.currentWindow + 1
                );
                this.currentPage = (this.currentWindow - 1) * this.visiblePages + 1;
                break;
        }

        this.render();
        this.scrollToTop();
        fetchNews(this.currentPage, this.activePage);
    }

    goToPage(pageNumber) {
        this.currentPage = pageNumber;
        this.currentWindow = Math.ceil(pageNumber / this.visiblePages);
        this.render();
        this.scrollToTop();
        fetchNews(this.currentPage, this.activePage);
    }

    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// Initialize the carousel
const carousel = new bootstrap.Carousel('#carouselExampleIndicators', {
    interval: 3000,
    ride: 'carousel'
});

// Fetch News Function
const fetchNews = async (page, query) => {
    console.log(`Fetching News for page ${page} with query: ${query}`);
    document.getElementById('pagination').style.display = 'flex';
    let url = query === 'home' 
        ? `https://backend-1096443573517.us-central1.run.app/get_news?page=${page}`
        : `https://backend-1096443573517.us-central1.run.app/get_news?query=${query}&page=${page}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        
        console.log(data['userId']);
        // Handle user login status
        const loginButton = document.getElementById('loginButton');
        const logoutButton = document.getElementById('logoutButton');
        const forYouSection = document.getElementById('ForYou');
        if (data['userId'] === '') {
            loginButton.style.display = 'block';
            logoutButton.style.display = 'none';
            forYouSection.style.display = 'none';
        } else {
            loginButton.style.display = 'none';
            logoutButton.style.display = 'block';
            forYouSection.style.display = 'block';
        }

        // Render articles from the fetched data
        renderArticles(data['news_data'].articles);

    } catch (error) {
        console.error("Error fetching news:", error);
    }
};

// Send Article Tag Function
function sendTag(title, url, description) {
    title = decodeURIComponent(title);
    url = decodeURIComponent(url);
    description = decodeURIComponent(description);


    console.log( title, url, description)

    fetch("https://backend-1096443573517.us-central1.run.app/send_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            url: url,
            description: description,
            query: newsPagination.activePage
        })
    })
    .then(response => response.json())
    .then(data => console.log("Response from backend:", data))
    .catch(error => console.error("Error:", error));
}

// Logout Function
const logout = async () => {
    try {
        const response = await fetch('https://backend-1096443573517.us-central1.run.app/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.href = 'index.html';
        } else {
            console.error('Logout failed:', response.statusText);
        }
    } catch (error) {
        console.error('Error during logout:', error);
    }
};


logoutButton.addEventListener("click", function(event) {
    event.preventDefault();
    // const query = searchInput.value;
    // fetchNews(1,query);
    logout();
});


// Initialize pagination
const newsPagination = new Pagination({
    totalPages: 15,
    visiblePages: 3,
    activePage: 'home'
});

// Centralized Event Handling
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (event) => {
        // Navigation links
        if (event.target.classList.contains('nav-link')) {
            event.preventDefault();
            
            // Remove 'active' from all nav links
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            event.target.classList.add('active');

            const pageText = event.target.textContent.toLowerCase();
            if (pageText !== 'for you') {
                newsPagination.changeActivePage(pageText);
            }
        }

        // Read More buttons
        if (event.target.classList.contains('read-more')) {
            event.preventDefault();
            const title = decodeURIComponent(event.target.getAttribute('data-title'));
            const url = decodeURIComponent(event.target.getAttribute('data-url'));
            const description = decodeURIComponent(event.target.getAttribute('data-description'));

            sendTag(title, url, description);
            window.open(url, '_blank');
        }
    });

    // 'For You' section specific handling
    document.getElementById('ForYou').addEventListener('click', async (event) => {
        event.preventDefault();
        document.getElementById('pagination').style.display = 'none';

        try {
            const response = await fetch('https://backend-1096443573517.us-central1.run.app/fetch_user_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                renderArticles(data['data'], false);
            } else {
                console.error('Failed to fetch data:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error occurred while fetching user data:', error);
        }
    });
});





document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const searchButton = document.getElementById("search");

    function handleSearch() {
        const query = searchInput.value;
        console.log("Search query:", query);
        // You can add logic here for what to do with the query
    }

    // Listen for input and click events, using the same function
    searchInput.addEventListener("input", handleSearch);
    searchButton.addEventListener("click", function(event) {
        event.preventDefault();
        const query = searchInput.value;
        fetchNews(1,query);
    });
});
