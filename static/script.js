
var timeleft = 5;
var downloadTimer = setInterval(function(){
  document.getElementById("countdown").innerHTML = "New quote coming in: " + timeleft;
  document.getElementById("new-quote").innerHTML = "Or click here for a new quote:";
  document.getElementById("selection").value = "Get New Quote";
  document.getElementById("selection").style.display = "inline";
  timeleft -= 1;
  if(timeleft <= 0){
    clearInterval(downloadTimer);
    window.location.href="/form";
  }
}, 1000);