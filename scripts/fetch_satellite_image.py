
from datetime import datetime
from sentinelhub import (
        SHConfig,
        DataCollection,
        SentinelHubRequest,
        BBox,
        bbox_to_dimensions,
        CRS,
        MimeType,
        )


class FetchSatelliteImage(SentinelHubRequest):
    def __init__(self, time_interval,
                 sat_type="s2",
                 bbox=None, resolution=8):

        if bbox == "befr":
            self.bbox = [4.989853, 43.557506, 5.234642, 43.395818]
        elif bbox == "mafr" and sat_type == "s2":
            self.bbox = [-1.13, 45.59, -0.95, 45.5035]
        elif bbox == "mafr" and sat_type == "s3":
            self.bbox = [-1.16, 45.62, -0.9, 45.46]
        elif bbox == "mefr":
            self.bbox = [4.75, 43.35, 5, 43.2]
        else:
            self.bbox = bbox

        self.resolution = resolution
        self.sat_type = sat_type

        print(f"bbox: {self.bbox}, for {sat_type} the {time_interval}")

        bbox, size = self.get_bbox_size()

        if size[0] > 2500 or size[1] > 2500:
            print(f"Error! {size}")
            exit(0)
       
        config = SHConfig("alex-profile")

        evalscript = self.get_eval_script()
        responses = self.get_responses()

        if sat_type == "s2":
            input_data = [self.get_input_data_S2(time_interval)]
        else:
            input_data = [self.get_input_data_S3(time_interval)]

        super().__init__(evalscript=evalscript,
                         input_data=input_data,
                         responses=responses,
                         bbox=bbox,
                         size=size,
                         config=config)

    # @staticmethod
    def get_bbox_size(self):
        aoi_bbox = BBox(bbox=self.bbox, crs=CRS.WGS84)
        aoi_size = bbox_to_dimensions(aoi_bbox, resolution=self.resolution)
        print(f"Image shape at {self.resolution} m resolution: {aoi_size} pixels") # noqa
        return aoi_bbox, aoi_size

    @staticmethod
    def get_input_data_S2(time_interval):
        return SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    name="s2",
                    service_url="https://sh.dataspace.copernicus.eu"
                    ),
                time_interval=time_interval)

    @staticmethod
    def get_input_data_S3(time_interval):
        return SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL3_OLCI.define_from(
                    name="s3",
                    service_url="https://sh.dataspace.copernicus.eu"
                    ),
                time_interval=time_interval)

    @staticmethod
    def get_responses():
        return [SentinelHubRequest.output_response("default", MimeType.PNG)]

    # @staticmethod
    def get_eval_script(self):
        if self.sat_type == "s2":
            return \
               """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["B02", "B03", "B04"]
                        }],
                        output: {
                            bands: 3
                        }
                    };
                }
                function evaluatePixel(sample) {
                    return [4 * sample.B04,
                            4 * sample.B03,
                            4 * sample.B02];
                }
                """
        else:
            return \
                    """
                //VERSION=3
                function setup() {
                  return {
                        input: ["B08","B05","B03", "dataMask"],
                        output: { bands: 4 }
                          };}
                  function evaluatePixel(sample) {
                   return [1.5 * sample.B08, 
                        1.5 * sample.B05, 
                        1.5 * sample.B03,
                        sample.dataMask];
                   }
                    """


if __name__ == '__main__':


    from argparse import ArgumentParser

    import matplotlib.pyplot as plt
    from sys import exit

    def valid_bbox(args):
        if len(args) == 4:
            return True

    def valid_date(arg):
        return True

    def valid_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as s:
            msg = "not a valid date: {0!r}".format(s)
            raise ArgumentTypeError(msg)

    parser = ArgumentParser()

    parser.add_argument("-s", "--satellite", type=int, default=3,
                        help="Select sentinel-2 or sentinel-3", choices=[2,3])

    selection_type = parser.add_mutually_exclusive_group(required=True)

    selection_type.add_argument("-i", "--site-id", type=str,
                                help="Select site ID.")

    selection_type.add_argument("-b", "--bbox", type=float,
                                help="Define a bbox", nargs='+')

    parser.add_argument("-d", "--date", type=valid_date, required=True,
                        help="Specify date")
   
    args = parser.parse_args()

    if args.bbox and not valid_bbox(args.bbox):
        raise Exception("Not a valid bbox.")
    elif args.bbox:
        bbox = args.bbox
    elif args.site_id:
        bbox = args.site_id
    else:
        exit(1)
    
    image_request = \
    FetchSatelliteImage(time_interval=args.date.strftime("%Y-%m-%d"),
                        bbox=bbox, sat_type=f"s{args.satellite}")

    image = image_request.get_data()[0]
    print(image)
    plt.imshow(image)
    plt.axis("off")
    plt.show()
