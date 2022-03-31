jQuery(document).ready(function($) {
  if ($("#google-reviews").length == 0) {
    return;
  }
  // Find a placeID via https://developers.google.com/places/place-id
  $("#google-reviews").googlePlaces({
    placeId: 'ChIJ2fnbJPTGK5AR2vsVYwf4dY8',
    // the following params are optional (default values)
    header: "", // html/text over Reviews
    footer: '', // html/text under Reviews block
    maxRows: 5, // max 5 rows of reviews to be displayed
    minRating: 4, // minimum rating of reviews to be displayed
    months: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    textBreakLength: "90", // length before a review box is set to max width
    shortenNames: true, // example: "Max Mustermann" -> "Max M."",
    moreReviewsButtonUrl: '', // url to Google Place reviews popup
    moreReviewsButtonLabel: '',
    writeReviewButtonUrl: '', // url to Google Place write review popup
    writeReviewButtonLabel: '',
    showProfilePicture: true
  });
});
