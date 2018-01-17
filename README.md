# Track scanner

[![Build Status](https://travis-ci.org/skyderby/track-segmentation.svg?branch=master)](https://travis-ci.org/skyderby/track-segmentation)

See it live: https://track-scanner.herokuapp.com/model/overview

API microservice that uses machine learning to:
* Find jump data from whole track that usually contains of walking, flying in aircraft, jump and canopy ride.
* Detect whether it was Basejumping or Skydiving


## Usage

As API endpoint - send POST request with csv data. Example:

```
curl -H "Content-Type: application/csv" -X POST https://track-scanner.herokuapp.com/prediction --data-binary "@./data/test/15-56-18.CSV"
```

Response:
```
{
  "activity": "skydive",
  "flight_starts_at": "2016-10-23T21:07:59.650"
  "deploy_at": "2016-10-23T21:09:55.400",
}
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
