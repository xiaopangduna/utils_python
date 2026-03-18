from lovely_utils.camera.calibration.generate_board.aruco_gridboard import ArUcoGridBoardGenerator


def test_ArUcoGridBoardGenerator_init():
    generator = ArUcoGridBoardGenerator()
    info = generator.info()
    assert info["markers_x"] == 1
    assert info["markers_y"] == 1
    assert info["total_markers"] == 1
    assert info["dictionary_id"] is not None
    assert isinstance(info["marker_ids"], list)
    assert len(info["marker_ids"]) == 1
    assert info["image_shape"][0] > 0 and info["image_shape"][1] > 0




# 如果直接运行此脚本，使用原始参数生成标定板
if __name__ == "__main__":
    # 使用原始的默认参数
    generator = ArUcoGridBoardGenerator(
        markers_x=1,
        markers_y=1,
        start_id=150,
        marker_length_mm=800,
        marker_sep_mm=200,
        margin_mm=100,
        dpi=72
    )
    
    # 生成并保存（使用默认前缀）
    generator.save()