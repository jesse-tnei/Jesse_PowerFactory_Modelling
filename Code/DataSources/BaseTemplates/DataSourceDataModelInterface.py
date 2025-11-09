class DataSourceDataModelInterface:
    def load_from_source_to_datamodel(self, source_data):
        """Load data from source into DataModel"""
        pass
    def export_from_datamodel_to_source(self, format_type):
        """Export DataModel data back to source format"""
        pass
    def orchestrate_source_data_loading(self, source_data, load_strategy="datamodel"):
        """Default orchestration - only supports datamodel strategy"""
        if load_strategy == "datamodel":
            return self.load_from_source_to_datamodel(source_data)
        else:
            raise NotImplementedError(f"Load strategy '{load_strategy}' not implemented in base class")