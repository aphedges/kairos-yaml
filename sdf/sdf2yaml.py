"""Convert SDF (0.93) to YAML for easier reading.

Omits some fields from the original JSON.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import yaml


def convert_sdf_to_yaml(data: Mapping[str, Any]) -> Mapping[str, Any]:
    yaml_obj = {}

    if "ta2" in data:
        yaml_obj["ta2"] = data["ta2"]

    if "schemas" in data:
        yaml_obj["schemas"] = []

        for sch in data["schemas"]:
            sc_obj = {
                "id": sch["@id"],
                "super": sch["super"],
                "name": sch["name"],
                "description": sch["description"],
                "steps": []
            }
            if "comment" in sch:
                sc_obj["comment"] = sch["comment"]

            if "slots" in sch:
                sc_obj["slots"] = []
                for slt in sch["slots"]:
                    sl_obj = {
                        "id": slt["@id"],
                        "roleName": slt["roleName"].split("/")[-1]
                    }

                    if "entityTypes" in slt:
                        sl_obj["constraints"] = [c.split("/")[-1] for c in slt["entityTypes"]]

                    opt_fields = ["name", "super", "reference", "provenance", "aka", "refvar"]
                    for field in opt_fields:
                        if field in slt:
                            sl_obj[field] = slt[field]

                    sc_obj["slots"].append(sl_obj)

            for stp in sch["steps"]:
                st_obj = {
                    "id": stp["@id"],
                    "primitive": stp["@type"].split("/")[-1],
                    "slots": []
                }

                opt_fields = [
                    "name", "description", "reference", "provenance", "comment", "aka",
                    "startTime", "endTime", "absoluteTime", "minDuration", "maxDuration"
                ]
                for field in opt_fields:
                    if field in stp:
                        st_obj[field] = stp[field]

                for slt in stp["participants"]:
                    sl_obj = {
                        "id": slt["@id"],
                        "name": slt["name"],
                        "role": slt["role"].split("/")[-1]
                    }
                    if "values" in slt:
                        if slt["values"] and len(slt["values"]) > 0:
                            sl_obj["values"] = slt["values"]

                    if "entityTypes" in slt:
                        sl_obj["constraints"] = [c.split("/")[-1] for c in slt["entityTypes"]]

                    opt_fields = ["reference", "provenance", "aka", "refvar"]
                    for field in opt_fields:
                        if field in slt:
                            sl_obj[field] = slt[field]

                    st_obj["slots"].append(sl_obj)

                sc_obj["steps"].append(st_obj)

            if "order" in sch:
                sc_obj["order"] = []
                for ord in sch["order"]:
                    od_obj = {}

                    opt_fields = ["before", "after", "overlaps", "container", "contained", "flags"]
                    for field in opt_fields:
                        if field in ord:
                            if field != "flags":
                                if isinstance(ord[field], list):
                                    od_obj[field] = [id.split("/")[-1] for id in ord[field]]
                                else:
                                    od_obj[field] = ord[field].split("/")[-1]
                            else:
                                od_obj[field] = ord[field]

                    sc_obj["order"].append(od_obj)

            # Prune or shorten ids for easier read
            sc_obj["id"] = sc_obj["id"].split("/")[-1]
            if "slots" in sc_obj:
                for slt in sc_obj["slots"]:
                    del slt["id"]
            for stp in sc_obj["steps"]:
                stp["id"] = stp["id"].split("/")[-1]
                for slt in stp["slots"]:
                    del slt["id"]

            yaml_obj["schemas"].append(sc_obj)

    if "primitives" in data:
        yaml_obj["primitives"] = []

        for prm in data["primitives"]:
            pm_obj = {
                "id": prm["@id"].split("/")[-1],
                "super": prm["super"],
                "name": prm["name"],
                "description": prm["description"],
                "slots": []
            }
            opt_fields = [
                "comment", "aka", "minDuration", "maxDuration"
            ]
            for field in opt_fields:
                if field in prm:
                    pm_obj[field] = prm[field]

            for slt in prm["slots"]:
                sl_obj = {
                    "id": slt["@id"].split("/")[-1],
                    "roleName": slt["roleName"]
                }

                if "entityTypes" in slt:
                    sl_obj["constraints"] = [c.split("/")[-1] for c in slt["entityTypes"]]

                opt_fields = ["reference", "provenance", "aka"]
                for field in opt_fields:
                    if field in slt:
                        sl_obj[field] = slt[field]

                pm_obj["slots"].append(sl_obj)

            yaml_obj["primitives"].append(pm_obj)

    return yaml_obj


def convert_files(json_file: Path, yaml_file: Path) -> None:
    with json_file.open() as file:
        json_data = json.load(file)

    yaml_data = convert_sdf_to_yaml(json_data)

    with yaml_file.open("w") as file:
        yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)


def main() -> None:
    """Converts JSON SDF into YAML schema."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--input-file", type=Path, required=True, help="Path to input SDF file."
    )
    p.add_argument("--output-file", type=Path, required=True, help="Path to output SDF schema.")
    args = p.parse_args()

    convert_files(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
