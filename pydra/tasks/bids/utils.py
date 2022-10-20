import dataclasses
import os

import pydra

__all__ = ["BIDSFileInfo", "BIDSDataReader"]


@dataclasses.dataclass
class BIDSFileInfo:
    """Parse components of a BIDS file.

    Examples
    --------

    Parse the main components of a BIDS file:

    >>> task = BIDSFileInfo().to_task(name="bids_file_info")
    >>> result = task(bids_file="sub-P01_ses-M00_T1w.nii.gz")
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    Additional source entities can be provided if specified as `output_entities`:

    >>> task = BIDSFileInfo(output_entities={"tracer": "trc"}).to_task(name="bids_file_info")
    >>> result = task(bids_file="sub-P01_trc-18FFDG_pet.nii.gz")
    >>> result.output.tracer
    '18FFDG'
    """

    output_entities: dict = dataclasses.field(default_factory=dict)

    def __call__(self, bids_file: os.PathLike):
        from ancpbids.utils import parse_bids_name

        parsed = parse_bids_name(os.fspath(bids_file))

        entities = parsed["entities"]
        suffix = parsed["suffix"]
        extension = parsed["extension"]

        # Extract participant ID
        subject_label = entities.get("sub")
        participant_id = f"sub-{subject_label}" if subject_label else None

        # Extract session ID
        session_label = entities.get("ses")
        session_id = f"ses-{session_label}" if session_label else None

        # Extract extra entities to provide as output.
        extra_entities = [
            entities.get(entity) for entity in self.output_entities.values()
        ]

        return tuple(
            [participant_id, session_id, entities, suffix, extension] + extra_entities
        )

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSFileInfoInput",
            fields=[("bids_file", os.PathLike)],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        # Default components parsed for all BIDS files.
        fields = [
            ("participant_id", str),
            ("session_id", str),
            ("entities", dict),
            ("suffix", str),
            ("extension", str),
        ] + [(entity, str) for entity in self.output_entities.keys()]

        return pydra.specs.SpecInfo(
            name="BIDSFileInfoOutput",
            fields=fields,
            bases=(pydra.specs.BaseSpec,),
        )

    def to_task(self, *args, **kwargs) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            *args,
            **kwargs,
        )


@dataclasses.dataclass
class BIDSDataReader:
    output_query: dict = dataclasses.field(
        default_factory=lambda: {
            "T1w": {"suffix": "T1w", "extension": ["nii", "nii.gz"]},
            "bold": {"suffix": "bold", "extension": ["nii", "nii.gz"]},
        },
    )

    def __call__(self, dataset_path: os.PathLike) -> dict:
        import ancpbids

        layout = ancpbids.BIDSLayout(ds_dir=os.fspath(dataset_path))

        return {
            key: layout.get(
                return_type="files",
                subject="*",
                session="*",
                **query,
            )
            for key, query in list(self.output_query.items())
        }

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSDataReaderInput",
            fields=[("dataset_path", os.PathLike)],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSDataReaderOutput",
            fields=[(key, str) for key in list(self.output_query.keys())],
            bases=(pydra.specs.BaseSpec,),
        )

    def to_task(self, *args, **kwargs) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            *args,
            **kwargs,
        )
