// Update the count down every 1 second
var countDown = function () {

    // Get todays date and time
    var now = new Date().getTime();

    // Find the distance between now an the count down date
    var distance = expiredDate.getTime() - now;

    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Display the result in the element with id="demo"
    if (days > 0) {
        countdown = days + "d " + hours + "h " + minutes + "m " + seconds + "s";
    }
    else {
        countdown = hours + "h " + minutes + "m " + seconds + "s";
    }

    document.getElementById("timer").innerHTML = countdown

    // If the count down is finished, write some text
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("timer").innerHTML = "EXPIRED";
        document.getElementById("paynow").style.visibility = "hidden";
    }

};
countDown();
var x = setInterval(countDown, 1000);