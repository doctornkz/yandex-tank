import time
import copy


def uts(dt):
    return int(time.mktime(dt.timetuple()))


class Decoder(object):
    """
    Decode metrics incoming from tank into points for InfluxDB client

    Parameters
    ----------
    parent_tags : dict
        common per-test tags
    tank_tag : basestring
        tank identifier tag
    uuid : basestring
        test id tag
    labeled : bool
        detailed stats for each label

    """
    def __init__(self, tank_tag, uuid, parent_tags):
        initial_tags = {
            "tank": tank_tag,
            "uuid": uuid
        }
        initial_tags.update(parent_tags)
        
        self.tags = initial_tags

    def set_uuid(self, id_):
        self.tags['uuid'] = id_


    def decode_aggregates(self, aggregated_data, gun_stats, prefix):
        ts = aggregated_data["ts"]
        points = list()
        # stats overall w/ __OVERALL__ label
        points += self.__make_points_for_label(
            ts,
            aggregated_data["overall"],
            "__OVERALL__",
            prefix,
            gun_stats
        )
        return points

    def decode_sfx_aggregates(self, aggregated_data, gun_stats, prefix):
        ts = aggregated_data["ts"]
        points = list()
        # stats overall w/ __OVERALL__ label
        # empty() + list() : I think to prevent None object
        points += self.__make_points_sfx_for_label(
            ts,
            aggregated_data["overall"],
            "__OVERALL__",
            prefix,
            gun_stats
        )
        return points

    def __make_points_for_label(self, ts, data, label, prefix, gun_stats):
        """
        Make a set of points for `this` label

        overall_quantiles, overall_meta, net_codes, proto_codes, 
        """
        label_points = list()

        label_points.extend(
            (
                # overall quantiles for label
                self.__make_points(
                    prefix + "overall_quantiles",
                    {"label": label},
                    ts,
                    self.__make_quantile_fields(data)
                ),
                # overall meta (gun status) for label
                self.__make_points(
                    prefix + "overall_meta",
                    {"label": label},
                    ts,
                    self.__make_overall_meta_fields(data, gun_stats)
                ),
                # net codes for label
                self.__make_points(
                    prefix + "net_codes",
                    {"label": label},
                    ts,
                    self.__make_netcodes_fields(data)
                ),
                # proto codes for label
                self.__make_points(
                    prefix + "proto_codes",
                    {"label": label},
                    ts,
                    self.__make_protocodes_fields(data)
                )
            )
        )

        return label_points


    def __make_points_sfx_for_label(self, ts, data, label, project, gun_stats):
        """
        Make a set of points for `this` label

        overall_quantiles, overall_meta, net_codes, proto_codes, 
        """
        label_points = list()

        label_points.extend(
                # overall quantiles for label
                self.__make_points(
                   "overall_quantiles",
                   project,
                   {"label": label},
                   ts,
                   self.__make_quantile_fields(data)
                ))

        label_points.extend(
                # overall meta (gun status) for labelmake_overall_meta_fields
                self.__make_points(
                    # overall_meta
                    "overall_meta",
                    project,
                    {"label": label},
                    ts,
                    self.__make_overall_meta_fields(data, gun_stats)
                ))

        label_points.extend(
                # net codes for label
                self.__make_code_points(
                    "net_codes",
                    project,
                    {"label": label},
                    ts,
                    self.__make_netcodes_fields(data)
                ))

        label_points.extend(
                #proto codes for label
                self.__make_code_points(
                   "proto_codes",
                   project,
                   {"label": label},
                   ts,
                   self.__make_protocodes_fields(data)
                ))
        

        return label_points

    @staticmethod
    def __make_quantile_fields(data):
        return {
            'q' + str(q): value / 1000.0
            for q, value in zip(data["interval_real"]["q"]["q"],
                                data["interval_real"]["q"]["value"])
        }

    @staticmethod
    def __make_overall_meta_fields(data, stats):
        
        
        return {
            "active_threads": stats["metrics"]["instances"],
            "RPS": data["interval_real"]["len"],
            "planned_requests": float(stats["metrics"]["reqps"]),
        }


    @staticmethod
    def __make_netcodes_fields(data):
        return {
            str(code): int(cnt)
            for code, cnt in data["net_code"]["count"].items()
        }

    @staticmethod
    def __make_protocodes_fields(data):
        return {
            str(code): int(cnt)
            for code, cnt in data["proto_code"]["count"].items()
        }

    def __make_points(self, measurement, project, additional_tags, ts, fields):
        tags = self.tags.copy()
        tags.update(additional_tags)
        tags.update({'project':project})        
        metrics = list()
        
        for field, value in fields.items(): 
            dimensions = copy.deepcopy(tags)
            dimensions.update({'field':field})
            metric = {'metric': measurement, 'timestamp': ts * 1000, 'dimensions':dimensions, 'value': value}
            metrics.append(metric)
        return metrics

    def __make_code_points(self, measurement, project, additional_tags, ts, fields):
        tags = self.tags.copy()
        tags.update(additional_tags)
        tags.update({'project':project})
        metrics = list()

        for field, value in fields.items():
            dimensions = copy.deepcopy(tags)
            dimensions.update({'code':field}) 
            metric = {'metric': measurement, 'timestamp': ts * 1000, 'dimensions':dimensions, 'value': value}
            metrics.append(metric)
        return metrics
