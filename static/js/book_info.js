function createElementClass(elementName, className) {
    const e = document.createElement(elementName);
    if (className) e.className = className;
    return e
}

function createDiv(className) {
    return createElementClass("div", className);
}

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

function createRatings(stars) {
    const theDiv = createDiv("review-stars");
    for (let i=0; i < stars; i++) {
        let theStar = createElementClass("i", "fas fa-star");
        theDiv.appendChild(theStar);
    }
    for (let i=stars; i < 5; i++) {
        let theStar = createElementClass("i", "far fa-star");
        theDiv.appendChild(theStar);
    }
    return theDiv
}

function createDetails(username, stars, time, content) {
    const colDiv = createDiv("col-11");
    const usernameDiv = createDiv("");
    const starsDiv = createRatings(stars);
    const timeDiv = createDiv("mb-2");
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
    let {content, profile_pic, stars, time, username} = review;
    const reviewDiv = createDiv("reviews row p-3");
    const pfpDiv = createPfp(profile_pic, username);
    const detailsDiv = createDetails(username, stars, time, content);
    const hrLine = createElementClass("hr", "mx-3");
    reviewDiv.appendChild(pfpDiv);
    reviewDiv.appendChild(detailsDiv);
    return reviewDiv;
}

function displayReviews(customerReviews, reviews) {
    for(let i=0; i < reviews.length; i++) {
        let reviewElement = createReview(reviews[i])
        let line = createElementClass("hr", "mx-3");
        customerReviews.appendChild(reviewElement);
        customerReviews.appendChild(line);
    }
}

function noReviews(customerReviews) {
    customerReviews.textContent = "No reviews have been written for this book.";
}

async function retrieveReviews() {
    const url = "/api/reviews/" + window.location.pathname.split("/")[2]
    try {
        const response = await fetch(url);
        if (response.ok) {
            const reviews = await response.json();
            return reviews;
        }
        else {
            throw new Error("API response not ok.");
        }
    }
    catch (err) {
        console.error(err);
    }
}

(async () => {
    const customerReviews = document.getElementById("customerReviews");
    const reviews = await retrieveReviews();

    if (reviews && reviews.length) {
        displayReviews(customerReviews, reviews);
    }
    else {
        noReviews(customerReviews);
    }
})();
