async function getReviews(book_id) {
    const url = "/api/reviews/" + book_id
    let response = await fetch(url)
    if (response.ok) {
        return await response.json();
    } else {
        throw new Error("API response not ok.");
    }
}

const buttons = document.querySelectorAll('[id^="btn_"]') // Select all modal bodies with IDs that start with reviewContents_
const buttonsArray = Array.prototype.slice.call(buttons) // Turn into array


buttonsArray.forEach(element => {
    let book_id = element.id.split('_')[1];
    element.addEventListener("click", async () => {
        let modalBody = document.getElementById('reviewContents_' + book_id)
        let reviewData = await getReviews(book_id)
        let reviews = reviewData.reviews
        console.log(reviews)
    });
});
