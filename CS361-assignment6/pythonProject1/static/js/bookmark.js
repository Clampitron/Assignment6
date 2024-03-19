$(".bookmark-btn").click(function() {
    const urlToBookmark = $(this).data("url"); // Make sure each bookmark button has a data-url attribute with the URL
    $.ajax({
        url: "/bookmark",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({url: urlToBookmark}),
        success: function(response) {
            alert("Bookmark added successfully!");
        },
        error: function(xhr, status, error) {
            alert("Error adding bookmark. Please try again.");
        }
    });
});