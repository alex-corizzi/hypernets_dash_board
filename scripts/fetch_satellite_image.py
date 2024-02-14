
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
        elif bbox == "mafr":
            self.bbox = [-1.13, 45.59, -0.96, 45.5035]
        else:
            self.bbox = bbox

        self.resolution = resolution
        self.sat_type = sat_type
        config = SHConfig("alex-profile")

        evalscript = self.get_eval_script()
        responses = self.get_responses()

        if sat_type == "s2":
            input_data = [self.get_input_data_S2(time_interval)]
        else:
            input_data = [self.get_input_data_S3(time_interval)]

        bbox, size = self.get_bbox_size()

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
                        input: [{
                            bands: ["B02", "B03", "B04"]
                        }],
                        output: {
                            bands: 3
                        }
                    };
                }
                function evaluatePixel(sample) {
                    return [2.5 * sample.B04,
                            2.1 * sample.B03,
                            1.5 * sample.B02];
                }
                """


if __name__ == '__main__':

    mafr_bbox = [-1.13, 45.59, -0.96, 45.5035]

    image_request = FetchSatelliteImage(time_interval="2023-07-02",
                                        bbox=mafr_bbox, sat_type="s3")

    image = image_request.get_data()[0]

    print(image)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.axis("off")
    fig.savefig("./image_sat.png")
