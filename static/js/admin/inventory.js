const buttons = document.querySelectorAll(".delete-book-button");

// Iterate through buttons and add event handler
Array.prototype.filter.call(buttons, button => {
  button.addEventListener("click", e => {
    document.getElementById(`toggleModal_${button.id.split("_")[1]}`).click();
  }, false);
});
