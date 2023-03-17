
# def add_stats_to_parquet_file(
#     path: str,
#     *,
#     new_path: str | None = None,
#     replace: bool = False,
# ):
#     if new_path is None:
#         if replace:
#             new_path = path + '_tmp'
#         else:
#             pass
    
#     df = pl.read_parquet(path)
#     df.write_parquet(new_path, statistics=True)
    
#     if replace:
#         shutil.move(new_path, path)
