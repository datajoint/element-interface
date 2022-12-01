import os
from pathlib import Path
from datetime import datetime


class EXTRACT:
    m_template = r"""
% Load Data
data = load('{scanfile}');
M = data.M;

% Input Paramaters
config = struct();
{parameters_list_string}

% Perform Extraction
output = extractor(M, config);
write({output_fullpath})
"""

    def __init__(self, scanfile_fullpath, parameters, output_dir) -> None:
        assert isinstance(self.parameters, dict)

        self.scanfile = Path(scanfile_fullpath)
        self.output_dir = Path(output_dir)
        self.parameters = parameters

    def write_matlab_run_script(self):
        """Compose the matlab script, run_extract.m, that would run the EXTRACT trigger."""

        assert self.scanfile.exists()

        self.output_fullpath = (
            Path(self.output_dir) / f"{self.scanfile.stem}_extract_output.mat",
        )

        m_file_content = self.m_template.format(
            **dict(
                parameters_list_string="\n".join(
                    [
                        f"config.{k} = '{v}';"
                        if isinstance(v, str)
                        else f"config.{k} = {str(v).lower()};"
                        if isinstance(v, bool)
                        else f"config.{k} = {v};"
                        for k, v in self.parameters.items()
                    ]
                ),
                scanfile=self.scanfile,
                output_fullpath=self.output_fullpath,
            )
        )

        self.m_file_fp = self.output_dir / "run_extract.m"

        with open(self.m_file_fp, "w") as f:
            f.write(m_file_content)

    def run(self):
        """Run run_extract.m script."""

        current_dir = Path.cwd()
        os.chdir(self.output_dir)

        run_status = {"execution_time": datetime.utcnow()}
        try:
            import matlab.engine

            eng = matlab.engine.start_matlab()
            eng.run_extract()
        except Exception as e:
            raise e
        finally:
            os.chdir(current_dir)

        run_status["execution_duration"] = (
            datetime.utcnow() - run_status["execution_time"]
        ).total_seconds()
        return run_status

    def load_results(self):
        from scipy.io import loadmat

        self.results = loadmat(self.output_fullpath)
