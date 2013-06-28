from parse.apps.stores.models import Store

st = Store.objects().get(objectId='lx8EJ2Rzmm')
st.active=True
st.categories=[]
st.city='Bronx'
st.coordinates=[40.42, -73.59]
st.country='US'
st.first_name="vandolf"
st.last_name="estrellado"
st.hours=[{"close_time":"1530","day":1,"open_time":"0700"},{"close_time":"1530","day":2,"open_time":"0700"},{"close_time":"2030","day":3,"open_time":"0530"},{"close_time":"2030","day":4,"open_time":"0530"},{"close_time":"1000","day":5,"open_time":"1000"}]
st.neighborhood="Dumbo"
st.phone_number="(718) 737-1994"
st.punches_facebook=5
st.rewards=[{"description":"Some description.","punches":"8","redemption_count":2,"reward_id":0,"reward_name":"Large Coffee"},{"description":"Choose from a Caffe Latte, Cappuccino, Chai Latte, Cafe Mocha, Vienna Coffee, and more!","punches":"12","redemption_count":1,"reward_id":1,"reward_name":"Espresso Drink of Your Choice"},{"description":"All our sandwiches come on a choice of Foccaccia, Baguette, or Ciabatta.","punches":"14","redemption_count":0,"reward_id":2,"reward_name":"Free Sandwich"}]
st.state="NY"
st.store_description="The Justice"
st.store_name="Brooklyn Cupcake"
st.street="1370 Virginia ave"
st.zip="10462"
st.store_timezone="America/New_York"

st.update()
