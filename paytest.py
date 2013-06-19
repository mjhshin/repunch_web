# tests with pyCurl

# get the access_token
curl https://api.sandbox.paypal.com/v1/oauth2/token \
 -H "Accept: application/json" \
 -H "Accept-Language: en_US" \
 -u "AaRn0BC74DY7UloGyRv8DBt8VmfK2QpDuTqQF_LYVTpejKftwlUCueD3jM7R:ELBn1BAQJOfiELEr04BA5NQieEpUe6MjT_dbSt0Vu0lA-8iuvefJfH8tUJPX" \
 -d "grant_type=client_credentials"

# output 
{"scope":"https://api.paypal.com/v1/payments/.* https://api.paypal.com/v1/vault/credit-card https://api.paypal.com/v1/vault/credit-card/.* openid","access_token":"rvVnR35YF7Q5ugoX3Or-nk.Lv16N05OuXbHbC-dCL78","token_type":"Bearer","app_id":"APP-80W284485P519543T","expires_in":28800}
 
 
# charge a credit card
curl -v https://api.sandbox.paypal.com/v1/payments/payment \
-H "Content-Type:application/json" \
-H "Authorization:Bearer rvVnR35YF7Q5ugoX3Or-nk.Lv16N05OuXbHbC-dCL78" \
-d '{
  "intent": "sale",
  "payer": {
    "payment_method": "credit_card",
    "funding_instruments": [
      {
        "credit_card": {
          "number": "4158740018304009",
          "type": "visa",
          "expire_month": 12,
          "expire_year": 2015,
          "cvv2": 905,
          "first_name": "Vandolf",
          "last_name": "Estrellado"
        }
      }
    ]
  },
  "transactions": [
    {
      "amount": {
        "total": "3.0",
        "currency": "USD"
      },
      "description": "Test payment"
    }
  ]
}'


# store a credit card
curl -v https://api.sandbox.paypal.com/v1/vault/credit-card \
-H 'Content-Type:application/json' \
-H 'Authorization:Bearer rvVnR35YF7Q5ugoX3Or-nk.Lv16N05OuXbHbC-dCL78' \
-d '{
 "payer_id":"sjsdh234js",
 "type":"visa",
 "number":"4158740018304009",
 "expire_month":"12",
 "expire_year":"2015",
 "first_name":"Vandolf",
 "last_name":"Estrellado"
}'

# output
{"id":"CARD-0CU24746JJ4821454KHBB5NA","valid_until":"2016-01-01T00:00:00Z","state":"ok","payer_id":"sjsdh234js","type":"visa","number":"xxxxxxxxxxxx4009","expire_month":"12","expire_year":"2015","first_name":"Vandolf","last_name":"Estrellado","links":[{"href":"https://api.sandbox.paypal.com/v1/vault/credit-card/CARD-0CU24746JJ4821454KHBB5NA","rel":"self","method":"GET"},{"href":"https://api.sandbox.paypal.com/v1/vault/credit-card/CARD-0CU24746JJ4821454KHBB5NA","rel":"delete","method":"DELETE"}]}

# charge a stored credit card
curl -v https://api.sandbox.paypal.com/v1/payments/payment \
-H 'Content-Type:application/json' \
-H 'Authorization: Bearer rvVnR35YF7Q5ugoX3Or-nk.Lv16N05OuXbHbC-dCL78' \
-d '{
  "intent":"sale",
  "payer":{
    "payment_method":"credit_card",
    "funding_instruments":[
      {
        "credit_card_token":{
          "credit_card_id":"CARD-0CU24746JJ4821454KHBB5NA",
          "payer_id":"sjsdh234js"
        }
      }
    ]
  },
  "transactions":[
    {
      "amount":{
        "total":"6.70",
        "currency":"USD"
      },
      "description":"This is the payment transaction description."
    }
  ]
}'
