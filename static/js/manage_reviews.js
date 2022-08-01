const buttons = document.querySelectorAll('[id^="btn_"]') // Select all buttons with IDs that start with btn_
const buttonsArray = Array.prototype.slice.call(buttons) // Turn into array of buttons

function createElementWithClasses (element, classes) {
    e = document.createElement(element)
    if (classes) {
        e.className = classes
    }
    return e
}

async function getReviews(book_id) {
    const url = "/api/reviews/" + book_id
    let response = await fetch(url)
    if (response.ok) {
        return await response.json();
    } else {
        throw new Error("API response not ok.");
    }
}

function displayReview(review) {
    reviewDiv = document.createElement("div")
    reviewDiv.className = "row p-3"
    reviewDiv.append(displayProfilePic(review), displayContents(review))
    return reviewDiv
}

function displayProfilePic(review) {
    let profilePicDiv = document.createElement("div")
    profilePicDiv.className = "col-1"

    let profilePic = new Image()
    profilePic.src = review.profile_pic
    profilePic.alt = review.username
    profilePic.className = "img-wrapper profile-picture"

    profilePicDiv.appendChild(profilePic)
    return profilePicDiv
}

function displayContents(review) {
    contentsContainer = createElementWithClasses("div", "col-10 flex-column")
    metadataContainer = createElementWithClasses("div", "d-inline-flex flex-row")
    
    let username = createElementWithClasses("div", "review-username p-2")
    let time = createElementWithClasses("div", "review-time p-2 ")
    let rating = createElementWithClasses("div", "p-2")
    let content = createElementWithClasses("div", "review-content p-2")
    
    username.textContent = review.username
    content.textContent = review.content
    time.textContent = review.time
    rating.textContent = review.stars + "/5 Stars"
    
    metadataContainer.append(username, time, rating)
    contentsContainer.append(metadataContainer, content)
    return contentsContainer
}

/* function deleteReview () {
    
} */

buttonsArray.forEach(element => {
    let book_id = element.id.split('_')[1];
    element.addEventListener("click", async () => {
        let modalBody = document.getElementById('reviewContents_' + book_id)
        let reviewData = await getReviews(book_id)
        let reviews = reviewData.reviews
        modalBody.replaceChildren() // Clear previous items to prevent duplicates        
        reviews.forEach(review => {
            modalBody.appendChild(displayReview(review))
            console.log(review)
        })
    });
});
