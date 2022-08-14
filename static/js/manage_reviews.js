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

function displayProfilePic(review) {
    let profilePicDiv = createElementWithClasses("div", "col-1")

    let profilePic = new Image()
    profilePic.src = review.profile_pic
    profilePic.alt = review.username
    profilePic.className = "img-wrapper profile-picture"

    profilePicDiv.appendChild(profilePic)
    return profilePicDiv
}

function displayContents(review) {
    let contentsContainer = createElementWithClasses("div", "col-10 flex-column") // Contains the metadata and the review content
    let metadataContainer = createElementWithClasses("div", "d-inline-flex flex-row") // Contains username, time, rating
    
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

function deleteButton(review, book_id) {
    let deleteButtonDiv = createElementWithClasses("div", "col-1")
    let deleteIcon = createElementWithClasses("i", "fa fa-trash actions-button")
    let button = createElementWithClasses("button", "btn")
    let csrfToken = document.getElementById(`csrf_token_${book_id}`).value

    let deleteButtonForm = document.createElement("form")
    deleteButtonForm.addEventListener("submit", async (e) => {
        let {message} = await deleteReview(book_id, review.user_id, csrfToken)
        alert(message)
    })
    

    button.appendChild(deleteIcon)
    deleteButtonForm.appendChild(button)
    deleteButtonDiv.append(deleteButtonForm)
    return deleteButtonDiv
}

function deleteReview(book_id, user_id, csrfToken) {
    const url = `/api/reviews/${book_id}?user_id=${user_id}`
    res = fetch(url, {
        method: 'DELETE',
        headers: {
            "X-CSRF-TOKEN": csrfToken,
            "Content-Type": "application/json",
        } 
    }).then(response => {
    if (! response.ok) {                           
        throw new Error('API response not OK.')
    } else {
        return response.json()
    }
    })
    return res 
}

function displayReview(review, book_id) {
    let reviewDiv = document.createElement("div")
    reviewDiv.className = "row p-3"
    reviewDiv.id = `user_${review.user_id}`
    reviewDiv.append(displayProfilePic(review), displayContents(review), deleteButton(review, book_id))
    return reviewDiv
}

function clearReviews(modalBody) {
    // Clear previous reviews in a modal body to prevent duplicates
    // I needed to make this to only delete the reviews so that the CSRF token is also not gone lol.
    modalBody.querySelectorAll('.row, .p-3').forEach(review => {
       modalBody.removeChild(review) 
    }) 
}

buttonsArray.forEach(element => {
    let book_id = element.id.split('_')[1];
    element.addEventListener("click", async () => {
        let modalBody = document.getElementById('reviewContents_' + book_id)
        let reviewData = await getReviews(book_id)
        let reviews = reviewData.reviews
        clearReviews(modalBody)
        reviews.forEach(review => {
            modalBody.appendChild(displayReview(review, book_id))
        })
    });
});
