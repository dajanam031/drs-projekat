var liveprice={
        "async":true,
        "scroosDomain":true,
        "url":"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cdogecoin%2Cethereum%2Clitecoin&vs_currencies=usd&include_24hr_change=true",

        "method":"GET",
        "headers":{}
}
   var btc=document.getElementById("bitcoin");
   var ltc=document.getElementById("litecoin");
   var eth=document.getElementById("ethereum");
   var doge=document.getElementById("dogecoin");
$.ajax(liveprice).done(function (response){

            btc.innerHTML = response.bitcoin.usd;
            ltc.innerHTML = response.litecoin.usd;
            eth.innerHTML = response.ethereum.usd;
            doge.innerHTML = response.dogecoin.usd;
});
