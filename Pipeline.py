import os

from Code.Formatting import FormatFile
from Code.Cleaning import CleanFile
from Code.Prep import PrepFile
from Code.Analysis import Analysis
from Code.Output import BuildOutput


class Pipeline:
    def __init__(self):
        Explorer = os.path.dirname(__file__)  
        FilePipeline = os.path.join(Explorer, "filepipeline")

        self.input_dir = os.path.join(FilePipeline, "A_InputData")
        self.formatted_dir = os.path.join(FilePipeline, "B_FormattedData")
        self.cleaned_dir = os.path.join(FilePipeline, "C_CleanData")
        self.prepped_dir = os.path.join(FilePipeline, "D_PreppedData")
        self.analysed_dir = os.path.join(FilePipeline, "E_AnalysedData")
        self.output_dir = os.path.join(FilePipeline, "F_OutputData")

    def Format(self):
        FormatFile(self.input_dir, self.formatted_dir)

    def Clean(self):
        CleanFile(self.formatted_dir, self.cleaned_dir)

    def PrepFile(self):
        PrepFile(self.cleaned_dir, self.prepped_dir)

    def Analyse(self):
        Analysis(self.prepped_dir, self.analysed_dir)

    def Output(self):
        BuildOutput(self.analysed_dir, self.output_dir)
        



APipeline = Pipeline()
APipeline.Format() #convert input excels to organised csvs
APipeline.Clean() #Fix errors
APipeline.PrepFile()
APipeline.Analyse() #
APipeline.Output()

