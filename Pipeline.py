import openpyxl
import os

ADFInputFile = "A_InputData\AdfInputData.xlsx"
PopulisInputFile_ = "A_InputData\PopulusInputData.xlsx"

from Code.Formatting import FormatFile
from Code.Breaking import BreakFile
from Code.Cleaning import CleanFile
from Code.Output import BuildOutput


class Pipeline:
    def __init__(self):
        Explorer = os.path.dirname(__file__)  
        FilePipeline = os.path.join(Explorer, "filepipeline")

        self.input_dir = os.path.join(FilePipeline, "A_InputData")
        self.formatted_dir = os.path.join(FilePipeline, "B_FormattedData")
        self.broken_dir = os.path.join(FilePipeline, "C_BrokenData")
        self.cleaned_dir = os.path.join(FilePipeline, "D_CleanData")
        self.output_dir = os.path.join(FilePipeline, "E_OutputData")

    def Format(self):
        FormatFile(self.input_dir, self.formatted_dir)

    def Break(self):
        BreakFile(self.formatted_dir, self.broken_dir)

    def Clean(self):
        CleanFile(self.broken_dir, self.clean_dir)

    def Output(self):
        BuildOutput(self.clean_dir, self.output_dir)



APipeline = Pipeline()
APipeline.Format() #convert input excels to organised csvs
APipeline.Break() #introduce errors
