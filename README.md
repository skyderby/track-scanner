# Track scanner

[![Build Status](https://travis-ci.org/skyderby/track-segmentation.svg?branch=master)](https://travis-ci.org/skyderby/track-segmentation)

See it live: https://track-scanner.herokuapp.com/model/overview

API microservice that uses machine learning to:
* Find jump data from whole track that usually contains of walking, flying in aircraft, jump and canopy ride.
* Detect whether it was Basejumping or Skydiving


## Usage

As API endpoint - send POST request with csv data. Example:

```
curl -H "Content-Type: application/csv" -X POST https://track-scanner.herokuapp.com/api/v1/scan --data-binary "@./data/test/15-56-18.CSV"
```

Response:
```
{
  "flight_starts_at": "2016-10-23T21:07:59.650"
  "deploy_at": "2016-10-23T21:09:55.400",
}
```

### Data format

File should contain only one line header an data.

Mandatory columns:
* time
* h_speed or velE and velN
* v_speed or velD

Example:
```
time,lat,lon,hMSL,velN,velE,velD,hAcc,vAcc,sAcc,gpsFix,numSV
2017-11-11T12:35:21.50Z,46.0227739,10.9207731,1437.665,1.10,0.20,1.98,88.354,126.603,9.74,3,6
2017-11-11T12:35:22.00Z,46.0229230,10.9207239,1406.920,0.10,0.15,0.72,28.727,31.846,1.59,3,7
2017-11-11T12:35:22.60Z,46.0229477,10.9207026,1391.510,-0.48,0.36,-0.19,16.099,18.884,0.68,3,7
2017-11-11T12:35:22.80Z,46.0229469,10.9206872,1390.263,-0.28,-0.08,-0.13,14.851,16.491,0.44,3,7
2017-11-11T12:35:23.00Z,46.0229441,10.9206742,1389.839,0.10,-0.02,-0.01,13.669,14.637,0.43,3,7
2017-11-11T12:35:23.20Z,46.0229451,10.9206800,1388.787,-0.02,0.05,0.06,12.713,13.236,0.33,3,7
2017-11-11T12:35:23.40Z,46.0229504,10.9206830,1386.630,0.10,-0.17,0.15,11.852,12.179,0.45,3,7
2017-11-11T12:35:23.60Z,46.0229508,10.9206818,1385.564,0.01,-0.16,0.19,11.070,11.311,0.38,3,7
2017-11-11T12:35:23.80Z,46.0229464,10.9206909,1386.406,0.08,-0.13,0.16,9.888,9.918,0.42,3,8
```
## Development

Want to contribute? Great!

To fix a bug or enhance an existing module, follow these steps:

* Fork the repo
* Create a new branch (`git checkout -b improve-feature`)
* Make the appropriate changes
* Commit your changes (`git commit -am 'Improve feature'`)
* Push to the branch (`git push origin improve-feature`)
* Create a Pull Request

## Bug / Feature Request

If you find a bug (the app couldn't handle the query and / or gave undesired results), kindly open an issue here by including data you sent to app and the expected result.

If you'd like to request a new function, feel free to do so by opening an issue here. Please include sample queries and their corresponding results.

## License

AGPLv3
