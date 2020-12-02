## RABT-rainfall

This project contains files to process and test rainfall data from Rest-and-Be-Thankful rain sensors via a weather api.

The HOBOnet sensors live on the RABT hillside and work with a HOBOnet Station Data Logger to send information to www.hobolink.com. The HOBOnet application has a data feed that sends rainfall data is generated from Weather Underground. Their api is at:  https://api.weather.com.

Data arrives from the api every 10 minutes from midnight and is processed by the Python into 15 minutes periods.
