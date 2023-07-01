from utils import *

class ReportGeneratorWorker(QObject):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = -55
        # the colors chould be adjusted
        self.divider_banner_color = (0.1, 0.44, 0.69)
        self.divider_text_color = (1,1,1)
        self.base_text_color = (0,0,0)

    def set_measurements(self, measurements:list):
        self.measurements = measurements
        self.min_concentration = min([i.concentration for i in self.measurements])
        self.max_concentration = max([i.concentration for i in self.measurements])

    def set_model_data(self, model_data):
        # this assumes that there is only 2 models
        # that fit the y = b0 + b1x model ==> only one model coeficient
        self.model_data = {"m1b0" : model_data[0].intercept_,
                           "m2b0" : model_data[1].intercept_,
                           "m1b1" : model_data[0].coef_[0],
                           "m2b1" : model_data[1].coef_[0],}
        
    def set_RMSE(self, rmse):
        self.rmse = rmse
        
    def set_model_fit(self, model_fit):
        self.model_fitness = model_fit        

    def set_CAC_plot(self, exported_image):
        self.CAC_plot = exported_image

    def set_dataview_plot(self, exported_image):
        self.dataview_plot = exported_image
        
    def generate(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            caption="Select a directory",
            directory=str(Path().absolute()),
            filter="PDF File (*.pdf)"
        )

        if not file_path:
            return
        
        canvas = Canvas(file_path, pagesize = A4)
        page_width, page_height = A4
        plot_width, plot_height = 500, 300
        font = "Times-Roman"
        

        def divider(string: str):
            canvas.setFillColorRGB(*self.divider_banner_color)
            canvas.setStrokeColorRGB(*self.divider_banner_color)
            canvas.roundRect(40 , page_height + self.offset, width = page_width - 80, height = 15, fill=True, radius= 5)
            canvas.setFillColorRGB(*self.divider_text_color)
            canvas.setStrokeColorRGB(*self.base_text_color)
            text = canvas.beginText(page_width/6 - 35, page_height + self.offset + 4)
            text.setFont(font, 12)
            text.textLine(string)
            canvas.drawText(text)
            canvas.setFillColorRGB(*self.base_text_color)
            self.offset -= 14
            # canvas.stringWidth(string, font, 12)
        
        def paragraph(title: str, *args: str):
            if abs(self.offset - (14 + 14.6*len(args))) >= page_height:
                canvas.showPage()
                self.offset = -55
            divider(title)
            
            text = canvas.beginText(50, page_height + self.offset)
            for line in args:
                text.textLine(line)
            self.offset -= 14.6*len(args) + 6
            canvas.drawText(text)
        
        def draw_plot(title: str, exported_plot):
            if abs(self.offset - (plot_height+10)) >= page_height:
                canvas.showPage()
                self.offset = -55
            with NamedTemporaryFile("r+b", delete=False, prefix="CAC_calculator", suffix='.png') as pl:
                exported_plot.parameters()['width'] = plot_width
                exported_plot.export(pl.name)
                divider(title)
                canvas.drawImage(pl.name, 50, page_height - plot_height + self.offset + 10, width=plot_width, height=plot_height)
                self.offset -= (plot_height+10)
                TEMP_FILENAME = pl.name
            # Using os.remove because the auto delete
            # caused OSError: Cannot open resource
            os.remove(TEMP_FILENAME)
            del TEMP_FILENAME

        paragraph("Sample text",
                f"CAC: {10**self.rmse.cac_data.get('cac_x', 0)[0]: .8f} mg/ml", # the 8 is because it can get small
                f"Minimum concentration in the experiment: {self.min_concentration}",
                f"Maximum concentration in the experiment: {self.max_concentration}")
        
        paragraph("Chosen model metrics",
                f"Model 1 parameters y = {self.model_data.get('m1b1', 0): .4f}x + {self.model_data.get('m1b0', 0): .4f}",
                f"Model 2 parameters y = {self.model_data.get('m2b1', 0): .4f}x + {self.model_data.get('m2b0', 0): .4f}",
                f"Models average root mean square error: {self.model_fitness.get('RMSE', 0): .5f}",
                f"Model average coeffcient of determiantion (R\u00b2): {self.model_fitness.get('R2', 0): .5f}",)

        draw_plot("CAC plot", self.CAC_plot)
        draw_plot("View on the data", self.dataview_plot)


        canvas.save()
        # reinitialising the offset
        # otherwise multiple report generation using
        # the same instance of the class would start the text generation lower
        self.offset = -55 
        print("Report generated")