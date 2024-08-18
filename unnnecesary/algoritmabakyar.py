class AngleFinder:
    def findAngle(self, hour, minute):
        hour_point = hour%12
        minute_point = minute%60
        raw_hour_angle = hour_point*30
        raw_minute_angle = minute_point*6
        hour_angle = abs(raw_hour_angle + 30*raw_minute_angle/360 - raw_minute_angle)
        return hour_angle


if __name__ == '__main__':
    angle_finder = AngleFinder()
    print(angle_finder.findAngle(12, 15))
        
        
        