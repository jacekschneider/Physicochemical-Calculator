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

    ## both plots will be required
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
        if file_path:
            canvas = Canvas(file_path, pagesize = A4)
            page_width, page_height = A4
            plot_width, plot_height = 500, 300
            font = "Times-Roman"
            

            def divider(string: str):
                canvas.setFillColorRGB(*self.divider_banner_color)
                canvas.setStrokeColorRGB(*self.divider_banner_color)
                canvas.rect(40 , page_height + self.offset, width = page_width - 80, height = 15, fill=True)
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

            # draw_plot("CAC plot", self.CAC_plot) # example usecase

            # draw_plot("CAC plot", self.dataview_plot)

            paragraph("Sample text",
                    f"CAC: {0.088}",
                    f"Mimimum concentration in the experiment: {self.min_concentration}",
                    f"Maximum concentration in the experiment: {self.max_concentration}")
            
            draw_plot("CAC plot", self.CAC_plot)
            
            # canvas.setTitle("CAC analysis")

            paragraph("Chosen model metrics",
                    f"Model parameters (y = ax + b) a: {0.088} b: {0.000011}",
                    f"Model Root Mean Square Error: {0.001}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",)
            canvas.save()
            # reinitialising the offset
            # otherwise multiple report generation using
            # the same instance of the class would start the text generation lower
            self.offset = -55 