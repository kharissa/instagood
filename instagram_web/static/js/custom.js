// Auto-close alerts 
window.setTimeout(function () {
    $(".alert").alert('close')
}, 2000);

// Initialize Masonry library
let grid = document.querySelector('.user-photos');
let masonry = new Masonry(grid, {
    itemSelector: 'li',
});

imagesLoaded(grid).on('progress', function () {
    // layout Masonry after each image loads
    masonry.layout();
});


const closeButton = document.querySelector('.lightbox-close');
const prevButton = document.querySelector('.lightbox-prev');
const nextButton = document.querySelector('.lightbox-next');
const donateButton = document.querySelector('.lightbox-donate');
const lightbox = document.querySelector('.lightbox');
const galleryItems = document.querySelectorAll('.gallery-item img');
const lightboxImage = document.querySelector('.lightbox-image');

let currentImageIndex;
let changeImageIndex;

function showImage(event) {
    // show lightbox
    lightbox.classList.remove('hidden');

    // replace lightbox image with clicked image 
    const elementClickedOn = event.target;
    const galleryItemParent = elementClickedOn.parentElement;

    // change slide index
    currentImageIndex = galleryItemParent.getAttribute('currentSlide');

    // Change lightbox to element clicked on html
    lightboxImage.innerHTML = galleryItemParent.innerHTML;

}

function nextImage(event) {
    event.preventDefault();

    if (currentImageIndex == galleryItems.length) {
        changeImageIndex = 1;
    } else {
        changeImageIndex = parseInt(currentImageIndex) + 1;
    }

    // Call next slide
    changeSlide(changeImageIndex);
}

function prevImage(event) {
    event.preventDefault();
    
    if (currentImageIndex == 1) {
        changeImageIndex = galleryItems.length;
    } else {
        changeImageIndex = parseInt(currentImageIndex) - 1;
    }

    // Call next slide
    changeSlide(changeImageIndex);
}

function changeSlide(n) {
    let match = document.querySelectorAll("li\[currentSlide\='" + n + "']");

    // Change lightbox to corresponding image
    lightboxImage.innerHTML = match[0].innerHTML;

    // Update slide index
    currentImageIndex = changeImageIndex;
}

function hideImage(event) {
    event.preventDefault();
    lightbox.classList.add('hidden');
}

function donate(event) {
    event.preventDefault();
    const elementClickedOn = event.target;
    const galleryItemParent = elementClickedOn.parentElement;
    console.log(elementClickedOn)
    console.log(galleryItemParent)
    currentImageIndex = galleryItemParent.getAttribute('currentSlide');
    console.log(currentImageIndex);
}

// For every gallery item, functionality to show image on lightbox on click
for (let index in galleryItems) {
    galleryItems[index].onclick = showImage;
}

// Hide lightbox upon close button click
closeButton.onclick = hideImage;
nextButton.onclick = nextImage;
prevButton.onclick = prevImage;
donateButton.onclick = donate;