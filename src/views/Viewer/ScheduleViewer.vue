<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="header">
          <h1>Schedule View</h1>
          <div class="header-actions">
            <button class="download-btn" @click="downloadSchedule">
              <i class="fas fa-download"></i>
              Download Schedule
            </button>
          </div>
        </div>

        <div class="schedule-container">
          <div class="lab-navigation">
            <button class="nav-btn" @click="previousLab">
              <i class="nav-icon"><</i>
            </button>
            <div class="lab-indicator">
              {{ selectedLab }}
            </div>
            <button class="nav-btn" @click="nextLab">
              <i class="nav-icon">></i>
            </button>
          </div>
          <div class="week-header">
            <div class="time-header">
              <div class="time-label">Time</div>
            </div>
            <div class="day-headers">
              <div class="day-header" v-for="(day, index) in weekDays" :key="index">
                <div class="day-name">{{ day.name }}</div>
                <div class="day-date">{{ day.date }}</div>
              </div>
            </div>
          </div>
          <div class="schedule-grid">
            <div class="time-column">
              <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                {{ time }}
              </div>
            </div>
            <div class="schedule-content">
              <div class="day-column" v-for="(day, dayIndex) in weekDays" :key="dayIndex">
                <div class="day-slots">
                  <div class="time-slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                    <div 
                      v-if="isTimeSlotWithinSchedule(day.name, time)"
                      class="schedule-item" 
                      :style="getScheduleStyle(day.name, time)"
                    >
                      <div 
                        v-if="isScheduleStart(day.name, time)" 
                        class="schedule-content"
                      >
                        <div class="schedule-title">{{ getScheduleTitle(day.name, time) }}</div>
                        <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                        <div class="schedule-details">{{ getScheduleDetails(day.name, time) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../../components/DashBoardSideBarViewer.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'ScheduleViewer',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: 'L201',
      laboratories: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', 
        '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM',
        '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM',
        '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM',
        '8:00 PM'
      ],
      weekDays: [],
      schedules: []
    }
  },
  created() {
    this.generateWeekDays()
    this.loadSchedules()
  },
  methods: {
    loadSchedules() {
      try {
        const savedSchedules = localStorage.getItem('labSchedules')
        if (savedSchedules) {
          const schedules = JSON.parse(savedSchedules)
          this.schedules = schedules.filter(schedule => schedule.labRoom === this.selectedLab)
        }
      } catch (error) {
        console.error('Error loading schedules:', error)
        this.schedules = []
      }
    },
    generateWeekDays() {
      const currentDate = new Date()
      const dayOfWeek = currentDate.getDay()
      const diff = currentDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
      const monday = new Date(currentDate.setDate(diff))
      
      const weekDays = []
      for (let i = 0; i < 6; i++) {
        const day = new Date(monday)
        day.setDate(monday.getDate() + i)
        weekDays.push({
          name: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][i],
          date: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        })
      }
      this.weekDays = weekDays
    },
    previousLab() {
      const currentIndex = this.laboratories.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.laboratories[currentIndex - 1]
        this.loadSchedules()
      }
    },
    nextLab() {
      const currentIndex = this.laboratories.indexOf(this.selectedLab)
      if (currentIndex < this.laboratories.length - 1) {
        this.selectedLab = this.laboratories[currentIndex + 1]
        this.loadSchedules()
      }
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        const isEndTimeSlot = timeSlot === schedule.endTime;
        
        return (timeSlotMinutes >= startMinutes && timeSlotMinutes < endMinutes) || isEndTimeSlot;
      });
    },
    isScheduleStart(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleStyle(dayName, timeSlot) {
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        
        return slotMinutes === startMinutes;
      });
      
      if (!schedule) return {};
      
      const startMinutes = this.convertTimeToMinutes(schedule.startTime);
      const endMinutes = this.convertTimeToMinutes(schedule.endTime);
      const firstSlotMinutes = this.convertTimeToMinutes('7:30 AM');
      
      // Calculate duration in 30-minute slots
      const durationSlots = Math.ceil((endMinutes - startMinutes) / 30);
      const height = durationSlots * 30 - 2; // Each slot is 30px high, subtract 2px for borders
      
      // Calculate top position
      const slotsFromStart = Math.floor((startMinutes - firstSlotMinutes) / 30);
      const topPosition = slotsFromStart * 30 + 1; // Add 1px offset for border
      
      return {
        position: 'absolute',
        top: `${topPosition}px`,
        height: `${height}px`,
        left: '2px',
        right: '2px',
        backgroundColor: schedule.color || '#FF4B75', // Lighter pink color
        borderRadius: '4px',
        padding: '6px 8px',
        overflow: 'hidden',
        zIndex: 1,
        color: '#fff',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      };
    },
    getScheduleTitle(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      if (!schedule) return '';
      return `${schedule.courseCode} (${schedule.types.join('/')})`;
    },
    getScheduleTime(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      return schedule ? `${schedule.startTime} - ${schedule.endTime}` : '';
    },
    getScheduleDetails(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      if (!schedule) return '';
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    convertTimeToMinutes(timeStr) {
      const [time, period] = timeStr.split(' ')
      let [hours, minutes] = time.split(':').map(Number)
      
      if (period === 'PM' && hours !== 12) {
        hours += 12
      } else if (period === 'AM' && hours === 12) {
        hours = 0
      }
      
      return hours * 60 + minutes
    },
    downloadSchedule() {
      // Implement schedule download functionality
      console.log('Downloading schedule...')
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.8rem;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.download-btn:hover {
  background-color: #c62f4d;
  transform: translateY(-1px);
}

.schedule-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.lab-navigation {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background-color: #DD385A;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background-color: #c62f4d;
}

.lab-indicator {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.week-header {
  display: flex;
  margin-bottom: 1rem;
}

.time-header {
  width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px 0 0 8px;
}

.day-headers {
  display: flex;
  flex: 1;
}

.day-header {
  flex: 1;
  padding: 1rem;
  text-align: center;
  background-color: #DD385A;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.day-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.95rem;
}

.day-date {
  font-size: 0.85rem;
  opacity: 0.9;
}

.schedule-grid {
  display: flex;
  height: calc(100vh - 450px);
  overflow-y: auto;
  background-color: #fff;
  position: relative;
  max-height: calc((30px * 52) + 50px); /* 26 time slots × 2 (30-min intervals) */
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  background-color: #f8f9fa;
  border-right: 1px solid #e0e0e0;
}

.schedule-content {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  position: relative;
  min-width: 120px;
  border-right: 1px solid #e0e0e0;
}

.day-column:last-child {
  border-right: none;
}

.time-slot {
  height: 30px; /* Changed to 30px for 30-minute intervals */
  padding: 0;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  color: #666;
  font-size: 0.85em;
  padding-right: 10px;
  box-sizing: border-box;
}

.schedule-item {
  position: absolute;
  left: 2px;
  right: 2px;
  background-color: #DD385A;
  border-radius: 4px;
  padding: 6px 8px;
  overflow: hidden;
  z-index: 1;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
  transform: scale(1.005);
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: #fff;
  margin: 0;
  line-height: 1.2;
}

.schedule-time {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.2;
  font-weight: 500;
}

.schedule-details {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.2;
  white-space: pre-line;
}

.day-slots {
  position: relative;
  height: 100%;
  min-height: calc(30px * 52);
}
</style>