/* Create elements general functions */
function createElementClass(elementName, className) {
    const e = document.createElement(elementName);
    if (className) e.className = className;
    return e
}

function createDiv(className) {
    return createElementClass("div", className);
}


/* Create review section components functions */
function createPfp(profilePic, username) {
    const colDiv = createDiv("col-1 profile-pic-col");
    const imgWrapper = createDiv("img-wrapper img-1-1");
    const img = createElementClass("img", "profile-pic");
    img.src = profilePic;
    img.alt = username;
    imgWrapper.appendChild(img);
    colDiv.appendChild(imgWrapper);
    return colDiv;
}

function createStars(stars) {
    const theDiv = createDiv("review-stars");
    for (let i=0; i < stars; i++) {
        let theStar = createElementClass("i", "fas fa-star");
        theDiv.appendChild(theStar);
        theDiv.appendChild(document.createTextNode(" "));
    }
    for (let i=stars; i < 5; i++) {
        let theStar = createElementClass("i", "far fa-star");
        theDiv.appendChild(theStar);
        theDiv.appendChild(document.createTextNode(" "));
    }
    return theDiv
}

function createDetails(username, stars, time, content) {
    const colDiv = createDiv("col-11");
    const usernameDiv = createDiv("review-username");
    const starsDiv = createStars(stars);
    const timeDiv = createDiv("mb-2 review-time");
    const contentDiv = createDiv("");
    usernameDiv.textContent = username;
    timeDiv.textContent = time;
    contentDiv.textContent = content;
    colDiv.appendChild(usernameDiv);
    colDiv.appendChild(starsDiv);
    colDiv.appendChild(timeDiv);
    colDiv.appendChild(contentDiv);
    return colDiv
}

function createReview(review) {
    const {content, profile_pic, stars, time, username} = review;
    const reviewDiv = createDiv("reviews row p-3");
    const pfpDiv = createPfp(profile_pic, username);
    const detailsDiv = createDetails(username, stars, time, content);
    reviewDiv.appendChild(pfpDiv);
    reviewDiv.appendChild(detailsDiv);
    return reviewDiv;
}

function createRatings(ratings) {
    const ratingsDetails = document.getElementById("ratingsDetails");
    const theNumSpan = createElementClass("span", "review-ratings");
    const theTextRow = createDiv("row px-3");
    const theTextDiv = createDiv("");
    const theTextSpan = createElementClass("span", "");
    const theStarRow = createDiv("row px-3");
    const theStarsDiv = createDiv("review-stars avg-ratings");
    ratingsDetails.insertAdjacentElement("afterbegin", theStarRow);
    ratingsDetails.insertAdjacentElement("afterbegin", theTextRow);
    theTextRow.appendChild(theTextDiv);
    theTextDiv.appendChild(theNumSpan);
    theTextDiv.appendChild(theTextSpan);
    theStarRow.appendChild(theStarsDiv);
    value = Math.round(ratings * 2);
    theNumSpan.textContent = (+ratings).toFixed(1);
    theTextSpan.textContent = " out of 5 stars";
    let x = 2;
    while (x <= value) {
        let theStar = createElementClass("i", "fas fa-star");
        theStarsDiv.appendChild(theStar);
        x += 2;
    }
    if (value+1 == x) {
        let theStar = createElementClass("i", "fas fa-star-half-alt");
        theStarsDiv.appendChild(theStar);
        x += 1
    }
    for (let i=x; i <= 10; i+=2) {
        let theStar = createElementClass("i", "far fa-star");
        theStarsDiv.appendChild(theStar);
    }
}


/* Display retrieved reviews functions */
function displayReviews(reviews, ratings) {
    const customerReviews = document.getElementById("customerReviews");
    for(let i=0; i < reviews.length; i++) {
        let reviewElement = createReview(reviews[i])
        let line = createElementClass("hr", "mx-3");
        customerReviews.appendChild(reviewElement);
        customerReviews.appendChild(line);
    }
    createRatings(ratings);
}

function noReviews() {
    const ratingsDetails = document.getElementById("ratingsDetails");
    const row = createDiv("row px-3");
    const message = createDiv("");
    row.appendChild(message);
    message.textContent = "No reviews have been written for this book."
    ratingsDetails.insertAdjacentElement("afterbegin", row);
}


/* Retrieve reviews from API function */
async function retrieveReviews() {
    const url = "/api/reviews/" + window.location.pathname.split("/")[2]
    try {
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        }
        else {
            throw new Error("API response not ok.");
        }
    }
    catch (err) {
        console.error(err);
    }
}


/* Main functions */
window.onload = () => {
    const redirectLoginButton = document.getElementById("redirectLoginButton");
    if (redirectLoginButton) {
        redirectLoginButton.addEventListener("click", () => {
            location.href = `/user/login?from=${encodeURIComponent(window.location.href)}`;
        });
    }
}

(async () => {
    const data = await retrieveReviews();

    if (data) {
        const {reviews, ratings} = data;
        if (reviews && reviews.length && ratings) {
            displayReviews(reviews, ratings);
        }
        else {
            noReviews();
        }
    }
    else {
        noReviews();
    }
})();
