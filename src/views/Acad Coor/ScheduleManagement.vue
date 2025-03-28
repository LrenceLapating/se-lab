<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="header">
          <h1>Scheduling Management</h1>
          <div class="header-actions">
            <button class="import-excel-btn" @click="showImportCoursesModal">
              <i class="fas fa-file-import"></i> Import Course Offerings
            </button>
            <button class="import-excel-btn" style="background-color: #f44336;" @click="clearAllSchedules">
              <i class="fas fa-trash"></i> Clear All Schedules
            </button>
            <button class="create-schedule-btn" @click="openCreateSchedule">
              <i class="fas fa-plus"></i> Create Schedule
            </button>
          </div>
        </div>

        <div class="schedule-container">
          <div class="lab-navigation">
            <div class="select-semester">
              <label>Select Semester:</label>
              <div class="select-wrapper">
                <select class="form-select" v-model="selectedSemester" @change="filterSchedulesBySemester">
                  <option value="" disabled selected>1st Sem</option>
                  <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                    {{ sem }}
                  </option>
                </select>
              </div>
            </div>
            <div class="center-navigation">
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
            <div class="navigation-spacer"></div>
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
                      :class="['schedule-item', getScheduleStatusClass(day.name, time)]" 
                      @click="openEditDeleteModal(day.name, time)"
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
        <div class="schedule-actions-footer">
          <button class="send-all-approval-btn" @click="sendAllForApproval">
            <i class="fas fa-paper-plane"></i>
            Send All Schedules for Approval
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- New Semester Modal -->
  <div class="modal" v-if="showNewSemesterModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>New Semester</h2>
        <button class="close-btn" @click="showNewSemesterModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Select Semester</label>
          <div class="select-wrapper">
            <select v-model="newSemester.semester" class="modal-dropdown">
              <option value="" disabled selected>Select Semester</option>
              <option value="1st">1st Semester</option>
              <option value="2nd">2nd Semester</option>
              <option value="summer">Summer</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>School Year</label>
          <div class="select-wrapper">
            <select v-model="newSemester.schoolYear" class="modal-dropdown">
              <option value="" disabled selected>Select School Year</option>
              <option value="2025">2025</option>
              <option value="2025-2026">2025-2026</option>
              <option value="2026-2027">2026-2027</option>
              <option value="2027">2027</option>
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showNewSemesterModal = false">Cancel</button>
        <button class="create-btn" @click="createNewSemester" :disabled="!isFormValid">Create</button>
      </div>
    </div>
  </div>

  <!-- Create Schedule Modal -->
  <div class="modal" v-if="showCreateScheduleModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Create Schedule</h2>
        <button class="close-btn" @click="showCreateScheduleModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-type-selector">
          <button 
            :class="['type-btn', { active: scheduleTypes.includes('Lab') }]" 
            @click="toggleScheduleType('Lab')"
          >Lab</button>
          <button 
            :class="['type-btn', { active: scheduleTypes.includes('Lec') }]" 
            @click="toggleScheduleType('Lec')"
          >Lec</button>
        </div>

        <div class="left-column">
          <div class="form-group">
            <label>Select Semester</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.semester" class="form-select">
                <option value="" disabled selected>Select Semester</option>
                <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                  {{ sem }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Select Degree Program | Year & Section</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.section" class="form-select">
                <option value="" disabled selected>Select Degree Program | Year & Section</option>
                <option v-for="section in sectionOptions" :key="section" :value="section">
                  {{ section }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Courses Offered</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.courseCode" class="form-select">
                <option value="" disabled selected>Select Course</option>
                <option v-for="course in availableCoursesOffered" :key="course.code" :value="course.code">
                  {{ course.code }} - {{ course.name }} ({{ course.semester }})
                </option>
                <option v-if="availableCoursesOffered.length === 0" disabled>
                  No available courses - all are in use
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="right-column">
          <div class="form-group">
            <label>Day</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.day" class="form-select" required>
                <option value="" disabled selected>Select Day</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Second Day (Optional)</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.secondDay" class="form-select">
                <option value="" selected>None</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Lab Room No.</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.labRoom" class="form-select">
                <option value="" disabled selected>Select Lab Room</option>
                <option v-for="room in labRooms" :key="room" :value="room">{{ room }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Start Time</label>
            <div class="time-picker">
              <select v-model="newSchedule.startHour" class="time-select">
                <option value="" disabled selected>--</option>
                <option v-for="hour in timeHours" :key="'start-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="newSchedule.startMinute" class="time-select">
                <option v-for="minute in timeMinutes" :key="minute" :value="minute">{{ minute }}</option>
              </select>
              <select v-model="newSchedule.startPeriod" class="period-select"
                      @change="validateStartTime">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>End Time</label>
            <div class="time-picker">
              <select v-model="newSchedule.endHour" class="time-select">
                <option value="" disabled selected>--</option>
                <option v-for="hour in timeHours" :key="'end-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="newSchedule.endMinute" class="time-select">
                <option v-for="minute in timeMinutes" :key="minute" :value="minute">{{ minute }}</option>
              </select>
              <select v-model="newSchedule.endPeriod" class="period-select"
                      @change="validateEndTime">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Instructor Name</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.instructorName" class="form-select" @change="handleInstructorSelect">
                <option value="" disabled selected>Select Instructor</option>
                <option v-for="instructor in instructors" :key="instructor" :value="instructor">
                  {{ instructor }}
                </option>
                <option value="add_new">+ Add New Instructor</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showCreateScheduleModal = false">Cancel</button>
        <button 
          class="create-btn" 
          @click="createSchedule" 
          :disabled="!isScheduleFormValid"
        >Create</button>
      </div>
    </div>
  </div>

  <!-- File Upload Modal -->
  <div class="modal" v-if="showFileUploadModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Import Course Offerings</h2>
        <button class="close-btn" @click="showFileUploadModal = false">×</button>
      </div>
      <div class="modal-body">
        <p class="import-instructions">
          Upload an Excel file containing course offerings. The file should include:
        </p>
        <ul class="import-requirements">
          <li><strong>Column A:</strong> Course Code (e.g., "FW123.23")</li>
          <li><strong>Column B:</strong> Course Name (e.g., "Ignatian Spirituality & Christian Life 1")</li>
          <li><strong>Column C:</strong> Year and Section (e.g., "IT-1A")</li>
          <li><strong>Column D:</strong> Semester (e.g., "1st Sem")</li>
        </ul>
        <p class="import-note">
          The first row should contain column headers. Matches exactly the format shown in the sample template.
        </p>
        <div class="file-upload-area" 
             @drop.prevent="handleFileDrop"
             @dragover.prevent
             @click="triggerFileInput">
          <input 
            type="file" 
            ref="fileInput" 
            style="display: none" 
            @change="handleFileSelect"
            accept=".csv,.xlsx">
          <div class="upload-icon">
            <i class="fas fa-file-upload"></i>
          </div>
          <p>Click or drag file to this area to upload</p>
          <p class="file-format-text">Formats accepted are .csv and .xlsx</p>
        </div>
        <div v-if="selectedFile" class="selected-file">
          <p><strong>Selected file:</strong> {{ selectedFile.name }}</p>
        </div>
        <div v-else class="sample-template">
          <p>If you do not have a file you can use the sample below:</p>
          <button class="download-sample-btn" @click="downloadSampleTemplate">
            <i class="fas fa-download"></i>
            Download Sample Template
          </button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showFileUploadModal = false">Cancel</button>
        <button class="import-btn" 
                @click="uploadFile" 
                :disabled="!selectedFile">Import Courses</button>
      </div>
    </div>
  </div>

  <!-- Edit/Delete Modal -->
  <div class="modal" v-if="showEditDeleteModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Schedule Options</h2>
        <button class="close-btn" @click="showEditDeleteModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-actions">
          <button class="edit-btn" @click="openEditSchedule">
            <i class=""></i>
            Edit Schedule
          </button>
          <button class="delete-btn" @click="confirmDelete">
            <i class=""></i>
            Delete Schedule
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Schedule Modal -->
  <div class="modal" v-if="showEditScheduleModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Edit Schedule</h2>
        <button class="close-btn" @click="showEditScheduleModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-type-selector">
          <button 
            :class="['type-btn', { active: editSchedule.types.includes('Lab') }]" 
            @click="toggleEditScheduleType('Lab')"
          >Lab</button>
          <button 
            :class="['type-btn', { active: editSchedule.types.includes('Lec') }]" 
            @click="toggleEditScheduleType('Lec')"
          >Lec</button>
        </div>

        <div class="left-column">
          <div class="form-group">
            <label>Select Semester <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.semester" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.semester }}</option>
                <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                  {{ sem }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Select Degree Program | Year & Section <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.section" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.section }}</option>
                <option v-for="section in sectionOptions" :key="section" :value="section">
                  {{ section }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Courses Offered <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.courseCode" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.courseCode }}</option>
                <option v-for="course in availableCoursesOffered" :key="course.code" :value="course.code">
                  {{ course.code }} - {{ course.name }} ({{ course.semester }})
                </option>
                <option v-if="availableCoursesOffered.length === 0" disabled>
                  No available courses - all are in use
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="right-column">
          <div class="form-group">
            <label>Day <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.day" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.day }}</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Second Day (Optional)</label>
            <div class="select-wrapper">
              <select v-model="editSchedule.secondDay" class="form-select">
                <option value="" selected>None</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Lab Room No. <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.labRoom" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.labRoom }}</option>
                <option v-for="room in labRooms" :key="room" :value="room">{{ room }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Start Time <span class="optional-text">(Optional - must update both start and end time together)</span></label>
            <div class="time-picker">
              <select v-model="editSchedule.startHour" class="time-select">
                <option value="">Current</option>
                <option v-for="hour in timeHours" :key="'start-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="editSchedule.startMinute" class="time-select">
                <option value="00">00</option>
                <option value="30">30</option>
              </select>
              <select v-model="editSchedule.startPeriod" class="period-select">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>End Time <span class="optional-text">(Optional - must update both start and end time together)</span></label>
            <div class="time-picker">
              <select v-model="editSchedule.endHour" class="time-select">
                <option value="">Current</option>
                <option v-for="hour in timeHours" :key="'end-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="editSchedule.endMinute" class="time-select">
                <option value="00">00</option>
                <option value="30">30</option>
              </select>
              <select v-model="editSchedule.endPeriod" class="period-select">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Instructor Name <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.instructorName" class="form-select" @change="handleEditInstructorSelect">
                <option value="">Keep current: {{ selectedSchedule.instructorName }}</option>
                <option v-for="instructor in instructors" :key="instructor" :value="instructor">
                  {{ instructor }}
                </option>
                <option value="add_new">+ Add New Instructor</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showEditScheduleModal = false">Cancel</button>
        <button 
          class="update-btn" 
          @click="updateSchedule" 
          :disabled="!isEditScheduleFormValid"
        >Update</button>
      </div>
    </div>
  </div>

  <!-- Confirm Delete Modal -->
  <div class="modal" v-if="showDeleteConfirmModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Confirm Delete</h2>
        <button class="close-btn" @click="showDeleteConfirmModal = false">×</button>
      </div>
      <div class="modal-body">
        <p>Are you sure you want to delete this schedule?</p>
        <div class="schedule-info">
          <p><strong>Course:</strong> {{ selectedSchedule?.courseCode }}</p>
          <p><strong>Section:</strong> {{ selectedSchedule?.section }}</p>
          <p><strong>Time:</strong> {{ getScheduleTime(selectedSchedule?.day, selectedSchedule?.startTime) }}</p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showDeleteConfirmModal = false">Cancel</button>
        <button class="delete-btn" @click="deleteSchedule">Delete</button>
      </div>
    </div>
  </div>

  <!-- Add New Instructor Modal -->
  <div class="modal" v-if="showAddInstructorModal">
    <div class="modal-content instructor-modal">
      <div class="modal-header instructor-modal-header">
        <h2>Add New Instructor</h2>
        <button class="close-btn" @click="showAddInstructorModal = false">×</button>
      </div>
      <div class="modal-body instructor-modal-body">
        <div class="form-group">
          <label>New Instructor Name</label>
          <input 
            type="text" 
            v-model="newInstructorName" 
            class="form-input instructor-input"
            placeholder="Enter instructor name"
            autofocus
          >
          <div class="input-icon">
            <i class="fas fa-user-plus"></i>
          </div>
        </div>
      </div>
      <div class="modal-footer instructor-modal-footer">
        <button class="cancel-btn instructor-cancel-btn" @click="showAddInstructorModal = false">Cancel</button>
        <button 
          class="add-btn instructor-add-btn" 
          @click="addNewInstructor" 
          :disabled="!newInstructorName.trim()"
        >
          <i class="fas fa-plus-circle"></i>
          Add Instructor
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx';
import DashBoardSidebar from '../../components/DashBoardSidebarAcadCoor.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'ScheduleManagement',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: 'L201',
      labs: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      allSchedules: [], // To store all schedules before filtering
      weekDays: [],
      selectedSemester: '1st Sem 2025-2026', // Default selected semester
      selectedDay: '',
      selectedSection: '',
      showNewSemesterModal: false,
      newSemester: {
        semester: '',
        schoolYear: ''
      },
      showCreateScheduleModal: false,
      scheduleTypes: [],
      semesterOptions: [
        '1st Sem 2025-2026',
        '2nd Sem 2025-2026',
        'Summer 2026',
        '1st Sem 2026-2027',
        '2nd Sem 2026-2027',
        'Summer 2027'
      ],
      sectionOptions: [
        'BSIT 1A', 'BSIT 1B',
        'BSCS 1A',
        'BSIT 2A', 'BSIT 2B',
        'BSCS 2A',
        'BSIT 3A', 'BSIT 3B',
        'BSCS 3A',
        'BSIT 4A', 'BSIT 4B',
        'BSCS 4A'
      ],
      coursesOffered: [], // Remove hardcoded courses, will be populated by imports
      days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      labRooms: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      timeHours: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], // Modified to match available hours
      timeMinutes: ['00', '30'], // Added for better time selection
      instructors: [
        'Instructor 1', 
        'Instructor 2', 
        'Instructor 3', 
        'Instructor 4', 
        'Instructor 5',
        'Instructor 6',
        'Instructor 7',
        'Instructor 8',
        'Instructor 9',
        'Instructor 10'
      ],
      newSchedule: {
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: ''
      },
      showFileUploadModal: false,
      selectedFile: null,
      showEditDeleteModal: false,
      showEditScheduleModal: false,
      showDeleteConfirmModal: false,
      selectedSchedule: null,
      editSchedule: {
        id: null,
        types: [],
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: ''
      },
      showAddInstructorModal: false,
      newInstructorName: ''
    }
  },
  methods: {
    previousLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.labs[currentIndex - 1]
      }
    },
    nextLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex < this.labs.length - 1) {
        this.selectedLab = this.labs[currentIndex + 1]
      }
    },
    generateWeekDays() {
      const today = new Date()
      const monday = new Date(today)
      monday.setDate(today.getDate() - today.getDay() + 1)

      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((name, index) => {
        const date = new Date(monday)
        date.setDate(monday.getDate() + index)
        
        // Format the date as "Mar 17, 2025" to match the design
        const formattedDate = date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric'
        });
        
        return {
          name,
          date: formattedDate
        }
      })
    },
    isTimeSlotInSchedule(timeSlot, startTime, endTime) {
      try {
        // Convert timeSlot, startTime, and endTime to minutes for easy comparison
        const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
        const startTimeMinutes = this.convertTimeToMinutes(startTime);
        const endTimeMinutes = this.convertTimeToMinutes(endTime);
        
        console.log('Time comparison:', 
          { timeSlot, timeSlotMinutes, 
            startTime, startTimeMinutes, 
            endTime, endTimeMinutes,
            isWithinRange: timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes
          }
        );
        
        // Check if timeSlot is within or at the start of the schedule
        return timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes;
      } catch (error) {
        console.error('Error checking if time slot is in schedule:', error);
        return false;
      }
    },
    convertTimeToMinutes(time) {
      try {
        // Parse time string (format: "HH:MM AM/PM")
        const [hourStr, minutePeriodStr] = time.split(':');
        if (!minutePeriodStr) {
          console.error('Invalid time format:', time);
          return 0;
        }
        
        const minutePeriod = minutePeriodStr.trim();
        const minuteStr = minutePeriod.split(' ')[0];
        const period = minutePeriod.split(' ')[1];
        
        if (!hourStr || !minuteStr || !period) {
          console.error('Invalid time components:', { hourStr, minuteStr, period, time });
          return 0;
        }
        
        let hour = parseInt(hourStr);
        const minute = parseInt(minuteStr);
        
        // Convert to 24-hour format
        if (period === 'PM' && hour < 12) hour += 12;
        if (period === 'AM' && hour === 12) hour = 0;
        
        const totalMinutes = hour * 60 + minute;
        // For debugging
        console.log(`Time conversion: "${time}" = ${hour}:${minute} (${period}) = ${totalMinutes} minutes`);
        
        // Return total minutes
        return totalMinutes;
      } catch (error) {
        console.error('Error converting time to minutes:', time, error);
        return 0;
      }
    },
    getScheduleForTimeSlot(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return null;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.find(schedule => {
        const matchesLab = schedule.labRoom === this.selectedLab;
        const matchesDay = schedule.day === dayName;
        const startTimeMinutes = this.convertTimeToMinutes(schedule.startTime);
        const matchesExactStartTime = timeSlotMinutes === startTimeMinutes;
        
        return matchesLab && matchesDay && matchesExactStartTime;
      }) || null;
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
        
        // Include the ending time slot as well
        return timeSlotMinutes >= startMinutes && timeSlotMinutes <= endMinutes;
      });
    },
    isScheduleStart(dayName, timeSlot) {
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
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleTitle(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return relevantSchedules[0].title;
    },
    getScheduleTime(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return `${relevantSchedules[0].startTime} - ${relevantSchedules[0].endTime}`;
    },
    getScheduleDetails(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      
      const schedule = relevantSchedules[0];
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    getScheduleStatusClass(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        // Include the ending time slot as well
        return slotMinutes >= startMinutes && slotMinutes <= endMinutes;
      });
      
      if (!schedule) return '';
      
      // Return the appropriate CSS class based on status
      switch (schedule.status) {
        case 'draft':
          return 'status-draft';
        case 'pending':
          return 'status-pending';
        case 'approved':
          return 'status-approved';
        default:
          return 'status-draft';
      }
    },
    getScheduleStyle(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        return slotMinutes >= startMinutes && slotMinutes < endMinutes;
      });
      
      if (!schedule) return {};
      
      // Use different colors for different schedule statuses
      let backgroundColor;
      switch (schedule.status) {
        case 'draft':
          backgroundColor = '#DD385A'; // Red
          break;
        case 'pending':
          backgroundColor = '#FFA500'; // Orange/Yellow
          break;
        case 'approved':
          backgroundColor = '#4CAF50'; // Green
          break;
        default:
          backgroundColor = '#DD385A';
      }
      
      return { backgroundColor };
    },
    handleNewSemester() {
      this.showNewSemesterModal = true;
    },
    handleSemesterChange() {
      if (this.selectedSemester === 'new') {
        this.handleNewSemester();
        this.selectedSemester = ''; // Reset selection
      }
    },
    createNewSemester() {
      // Here you'll add the logic to create the new semester
      console.log('Creating new semester:', this.newSemester);
      this.showNewSemesterModal = false;
      // Reset form
      this.newSemester = {
        semester: '',
        schoolYear: ''
      };
    },
    openCreateSchedule() {
      this.showCreateScheduleModal = true;
    },
    createSchedule() {
      // Validate fields
      if (!this.newSchedule.semester || !this.newSchedule.day || !this.newSchedule.labRoom || !this.newSchedule.courseCode || this.scheduleTypes.length === 0) {
        alert('Please fill in all required fields and select at least one schedule type');
        return;
      }
      
      if (!this.newSchedule.startHour || !this.newSchedule.endHour) {
        alert('Please select start and end times');
        return;
      }
      
      // Format time strings
      const startTime = `${this.newSchedule.startHour}:${this.newSchedule.startMinute} ${this.newSchedule.startPeriod}`;
      const endTime = `${this.newSchedule.endHour}:${this.newSchedule.endMinute} ${this.newSchedule.endPeriod}`;
      
      // Convert to minutes for validation
      const startMinutes = this.convertTimeToMinutes(startTime);
      const endMinutes = this.convertTimeToMinutes(endTime);
      const minStartTime = this.convertTimeToMinutes('7:30 AM');
      const maxEndTime = this.convertTimeToMinutes('8:00 PM');
      
      if (startMinutes < minStartTime) {
        alert('Schedule cannot start before 7:30 AM');
        return;
      }
      
      if (endMinutes > maxEndTime) {
        alert('Schedule cannot end after 8:00 PM');
        return;
      }
      
      if (endMinutes <= startMinutes) {
        alert('End time must be after start time');
        return;
      }

      // Check for overlapping schedules in the SAME SEMESTER, DAY, AND LAB ROOM
      const existingSchedules = this.allSchedules.filter(schedule => 
        schedule.semester === this.newSchedule.semester &&
        schedule.day === this.newSchedule.day && 
        schedule.labRoom === this.newSchedule.labRoom &&
        !schedule.isDeleted
      );

      console.log('All existing schedules in this SEMESTER/LAB/DAY:', existingSchedules);
      console.log('Checking for conflicts with new schedule in semester:', this.newSchedule.semester);

      // ======= IMPROVED OVERLAP DETECTION LOGIC =========
      let hasOverlap = false;
      for (const schedule of existingSchedules) {
        // Convert string times to minutes for precise comparison
        const existingStartMinutes = this.convertTimeToMinutes(schedule.startTime);
        const existingEndMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        console.log('Checking potential overlap between:');
        console.log(`- New schedule: ${startTime} to ${endTime} (${startMinutes} to ${endMinutes} minutes)`);
        console.log(`- Existing: ${schedule.startTime} to ${schedule.endTime} (${existingStartMinutes} to ${existingEndMinutes} minutes)`);
        
        // Case 1: New schedule starts during existing schedule
        // (newStart >= existingStart && newStart < existingEnd)
        const newStartsDuringExisting = 
          startMinutes >= existingStartMinutes && 
          startMinutes < existingEndMinutes;
        
        // Case 2: New schedule ends during existing schedule
        // (newEnd > existingStart && newEnd <= existingEnd)
        const newEndsDuringExisting = 
          endMinutes > existingStartMinutes && 
          endMinutes <= existingEndMinutes;
        
        // Case 3: New schedule completely contains existing schedule
        // (newStart <= existingStart && newEnd >= existingEnd)
        const newContainsExisting = 
          startMinutes <= existingStartMinutes && 
          endMinutes >= existingEndMinutes;
        
        // No overlap only when:
        // 1. New schedule ends at or before existing schedule starts
        // 2. OR New schedule starts at or after existing schedule ends
        const noOverlap = 
          endMinutes <= existingStartMinutes || 
          startMinutes >= existingEndMinutes;
        
        // For debugging
        const overlapResult = {
          newStartsDuringExisting,
          newEndsDuringExisting,
          newContainsExisting,
          noOverlap,
          hasOverlap: !noOverlap
        };
        
        console.log('Overlap check results:', overlapResult);
        
        if (!noOverlap) {
          hasOverlap = true;
          break;
        }
      }

      if (hasOverlap) {
        alert(`Cannot create schedule at this time slot. There is already a schedule for ${this.newSchedule.day} in ${this.newSchedule.labRoom} that overlaps with ${startTime} - ${endTime}.`);
        return;
      }
      
      // Check for overlap on the second day if it's selected
      if (this.newSchedule.secondDay) {
        const secondDaySchedules = this.allSchedules.filter(schedule => 
          schedule.semester === this.newSchedule.semester &&
          schedule.day === this.newSchedule.secondDay && 
          schedule.labRoom === this.newSchedule.labRoom &&
          !schedule.isDeleted
        );
        
        console.log('All existing schedules for second day:', secondDaySchedules);
        
        // Check for overlap on second day
        hasOverlap = false;
        for (const schedule of secondDaySchedules) {
          const existingStartMinutes = this.convertTimeToMinutes(schedule.startTime);
          const existingEndMinutes = this.convertTimeToMinutes(schedule.endTime);
          
          // Check for overlap using the same logic as for the main day
          const noOverlap = 
            endMinutes <= existingStartMinutes || 
            startMinutes >= existingEndMinutes;
          
          if (!noOverlap) {
            hasOverlap = true;
            break;
          }
        }
        
        if (hasOverlap) {
          alert(`Cannot create schedule at this time slot. There is already a schedule for ${this.newSchedule.secondDay} in ${this.newSchedule.labRoom} that overlaps with ${startTime} - ${endTime}.`);
          return;
        }
      }
      
      const selectedCourse = this.availableCoursesOffered.find(course => course.code === this.newSchedule.courseCode);
      const courseName = selectedCourse ? selectedCourse.name : '';
      
      const durationMinutes = this.calculateDurationMinutes(startTime, endTime);
      
      const newSchedule = {
        id: Date.now().toString(),
        title: `${this.newSchedule.courseCode} (${this.scheduleTypes.join('/')})`,
        details: `${courseName}\n${this.newSchedule.section}\n${this.newSchedule.instructorName}`,
        semester: this.newSchedule.semester,
        section: this.newSchedule.section,
        courseCode: this.newSchedule.courseCode,
        courseName: courseName,
        day: this.newSchedule.day,
        labRoom: this.newSchedule.labRoom,
        instructorName: this.newSchedule.instructorName,
        startTime: startTime,
        endTime: endTime,
        duration: durationMinutes,
        types: [...this.scheduleTypes],
        color: '#DD385A',
        status: 'draft',
        secondDay: this.newSchedule.secondDay
      };
      
      try {
        // Get existing schedules from acad_coor_schedules
        let existingSchedules = JSON.parse(localStorage.getItem('acad_coor_schedules') || '[]');
        
        // Handle both array and object with schedules property
        if (existingSchedules.schedules) {
          existingSchedules = existingSchedules.schedules;
        }
        
        // Make sure existingSchedules is an array
        if (!Array.isArray(existingSchedules)) {
          existingSchedules = [];
        }
        
        // Add new schedule to existing schedules
        existingSchedules.push(newSchedule);
        
        // If second day is selected, create a duplicate schedule for that day
        if (this.newSchedule.secondDay) {
          const secondDaySchedule = {
            ...newSchedule,
            id: Date.now().toString() + '-second',
            day: this.newSchedule.secondDay
          };
          existingSchedules.push(secondDaySchedule);
        }
        
        // Save only to acad_coor_schedules
        localStorage.setItem('acad_coor_schedules', JSON.stringify(existingSchedules));
        
        // Update the component's schedules
        this.allSchedules = existingSchedules;
        
        // Refresh the schedules display to show only draft schedules
        this.filterSchedulesBySemester();
        
        // Close the modal and reset form
        this.showCreateScheduleModal = false;
        this.resetScheduleForm();
        
        alert('Schedule created successfully! It will be visible in other dashboards after approval.');
      } catch (error) {
        console.error('Error saving schedule:', error);
        alert('Error creating schedule. Please try again.');
      }
    },
    
    calculateDurationMinutes(startTime, endTime) {
      try {
        const startMinutes = this.convertTimeToMinutes(startTime);
        const endMinutes = this.convertTimeToMinutes(endTime);
        
        const duration = endMinutes - startMinutes;
        console.log(`Duration from ${startTime} to ${endTime}: ${duration} minutes`);
        
        return duration;
      } catch (error) {
        console.error('Error calculating duration:', error);
        return 60;
      }
    },
    
    saveSchedulesToStorage() {
      try {
        // Get existing schedules from localStorage
        let existingSchedules = JSON.parse(localStorage.getItem('acad_coor_schedules') || '[]');
        
        // Handle both array and object with schedules property
        if (existingSchedules.schedules) {
          existingSchedules = existingSchedules.schedules;
        }
        
        // Make sure existingSchedules is an array
        if (!Array.isArray(existingSchedules)) {
          existingSchedules = [];
        }
        
        // Filter out deleted schedules from existing
        const activeSchedules = existingSchedules.filter(schedule => !schedule.isDeleted);
        
        // Update or add new schedules
        this.allSchedules.forEach(newSchedule => {
          const existingIndex = activeSchedules.findIndex(s => s.id === newSchedule.id);
          
          if (existingIndex !== -1) {
            // Update existing schedule
            activeSchedules[existingIndex] = {
              ...activeSchedules[existingIndex],
              ...newSchedule
            };
          } else {
            // Add new schedule
            activeSchedules.push(newSchedule);
          }
        });
        
        // Save to localStorage as a simple array
        localStorage.setItem('acad_coor_schedules', JSON.stringify(activeSchedules));
        
        // Update the component's schedules
        this.allSchedules = activeSchedules;
        this.filterSchedulesBySemester();
        
        console.log('Schedules saved successfully');
      } catch (error) {
        console.error('Error saving schedules:', error);
      }
    },
    
    loadSchedulesFromStorage() {
      try {
        // Load from acad_coor_schedules for draft schedules
        let schedules = [];
        const acadCoorSchedulesStr = localStorage.getItem('acad_coor_schedules');
        
        if (acadCoorSchedulesStr) {
          let parsedData = JSON.parse(acadCoorSchedulesStr);
          
          // Handle both array and object with schedules property
          if (parsedData.schedules) {
            parsedData = parsedData.schedules;
          }
          
          // Make sure parsedData is an array
          if (Array.isArray(parsedData)) {
            schedules = [...schedules, ...parsedData];
          }
        }
        
        // Remove duplicates based on schedule ID
        const uniqueSchedules = [];
        const seen = new Set();
        schedules.forEach(schedule => {
          if (!seen.has(schedule.id)) {
            seen.add(schedule.id);
            uniqueSchedules.push(schedule);
          }
        });
        
        this.allSchedules = uniqueSchedules;
        console.log('Loaded schedules from localStorage:', this.allSchedules.length);
        
        // Apply initial filtering based on selected semester
        this.filterSchedulesBySemester();
      } catch (error) {
        console.error('Error loading schedules from localStorage:', error);
        this.schedules = [];
        this.allSchedules = [];
      }
    },
    resetScheduleForm() {
      this.scheduleTypes = [];
      this.newSchedule = {
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: ''
      };
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },
    handleFileDrop(event) {
      const file = event.dataTransfer.files[0];
      const allowedTypes = ['.xlsx', '.csv'];
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      
      if (allowedTypes.includes(fileExtension)) {
        this.selectedFile = file;
      } else {
        alert('Please upload a valid Excel or CSV file.');
      }
    },
    downloadSampleTemplate() {
      // Create a workbook with a worksheet
      const wb = XLSX.utils.book_new();
      
      // Create sample data exactly matching the format in the screenshot
      const sampleData = [
        { A: "Course Code", B: "Course Name", C: "Year and Section", D: "Semester" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "IT-1A", D: "1st Sem" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "IT-1B", D: "1st Sem" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "CS-1A", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "IT-1A", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "IT-1B", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "CS-1A", D: "1st Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "IT-1A", D: "2nd Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "IT-1B", D: "2nd Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "CS-1A", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "IT-1A", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "IT-1B", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "CS-1A", D: "2nd Sem" }
      ];
      
      // Create a worksheet from the data
      const ws = XLSX.utils.json_to_sheet(sampleData, { skipHeader: true });
      
      // Set column widths
      const colWidths = [
        { wch: 15 }, // A: Course Code
        { wch: 40 }, // B: Course Name
        { wch: 15 }, // C: Year and Section
        { wch: 15 }  // D: Semester
      ];
      
      ws['!cols'] = colWidths;
      
      // Add the worksheet to the workbook
      XLSX.utils.book_append_sheet(wb, ws, "Course Offerings");
      
      // Generate Excel file
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      
      // Convert to Blob
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'course_offerings_template.xlsx';
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    },
    uploadFile() {
      if (!this.selectedFile) {
        alert('Please select a file to upload.');
        return;
      }
      
      const file = this.selectedFile;
      console.log('Processing file:', file.name);
      
      // Check file extension
      const fileExt = file.name.split('.').pop().toLowerCase();
      if (fileExt !== 'xlsx' && fileExt !== 'csv') {
        alert('Please upload an Excel (.xlsx) or CSV (.csv) file.');
        return;
      }
      
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          // Use a try/catch block to handle any parsing errors
          let wb;
          
          if (fileExt === 'csv') {
            // Handle CSV files
            const csvData = e.target.result;
            wb = XLSX.read(csvData, { type: 'string' });
          } else {
            // Handle Excel files
            const data = e.target.result;
            wb = XLSX.read(data, { type: 'binary' });
          }
          
          // Get the first sheet
          const firstSheetName = wb.SheetNames[0];
          if (!firstSheetName) {
            throw new Error('No worksheet found in file');
          }
          
          const ws = wb.Sheets[firstSheetName];
          
          // Use row object array format (each row is an object with keys)
          const rawData = XLSX.utils.sheet_to_json(ws);
          console.log('Raw data from Excel:', rawData);
          
          if (!rawData || rawData.length === 0) {
            alert('No data found in the file or invalid format.');
            return;
          }
          
          // Process the course data
          const importedCourses = [];
          let hasErrors = false;
          
          rawData.forEach((row, index) => {
            // Get keys from the first row (expected "Course Code", "Course Name", "Year and Section")
            const keys = Object.keys(row);
            const courseCodeKey = keys.find(k => k.toLowerCase().includes('code'));
            const courseNameKey = keys.find(k => k.toLowerCase().includes('name'));
            const sectionKey = keys.find(k => k.toLowerCase().includes('section') || k.toLowerCase().includes('year'));
            const semesterKey = keys.find(k => k.toLowerCase().includes('semester'));
            
            if (!courseCodeKey || !courseNameKey) {
              console.warn(`Row ${index + 1} missing required columns:`, row);
              hasErrors = true;
              return;
            }
            
            const code = row[courseCodeKey];
            const name = row[courseNameKey];
            const section = sectionKey ? row[sectionKey] : null;
            const semester = semesterKey ? row[semesterKey] : null;
            
            if (!code || !name) {
              console.warn(`Row ${index + 1} has empty code or name:`, row);
              return;
            }
            
            importedCourses.push({
              code: code.toString(),
              name: name.toString(),
              section: section ? section.toString() : '',
              semester: semester ? semester.toString() : ''
            });
          });
          
          if (importedCourses.length === 0) {
            if (hasErrors) {
              alert('Could not import courses due to format errors. Please check your file structure.');
            } else {
              alert('No valid courses found in the file.');
            }
            return;
          }
          
          // Successfully processed data
          console.log('Processed courses:', importedCourses);
          
          // Add to courses offered
          const importResult = this.importCoursesOffered(importedCourses);
          
          // Close modal and clear selection
          this.showFileUploadModal = false;
          this.selectedFile = null;
          
          // Show success message with alert instead of toast
          if (importResult.newCourses === 0) {
            alert('No courses were found to import from the Excel file.');
          } else {
            alert(`Successfully imported ${importResult.newCourses} course${importResult.newCourses !== 1 ? 's' : ''}! These courses will be available even after refresh or logout.`);
          }
          
        } catch (error) {
          console.error('Error processing file:', error);
          alert('Error processing the file: ' + (error.message || 'Invalid file format'));
        }
      };
      
      reader.onerror = () => {
        console.error('Error reading file');
        alert('Error reading the file. Please try again.');
      };
      
      // Read the file based on its type
      if (fileExt === 'csv') {
        reader.readAsText(file);
      } else {
        reader.readAsBinaryString(file);
      }
    },
    importCoursesOffered(coursesData) {
      if (!Array.isArray(coursesData) || coursesData.length === 0) {
        console.warn('No courses to import or invalid data format');
        return { newCourses: 0, updatedCourses: 0 };
      }
      
      console.log('Starting import of courses:', coursesData);
      console.log('Current courses in system:', this.coursesOffered);
      
      // Import all courses from Excel as new entries
      const importedCourses = [];
      
      coursesData.forEach((course, index) => {
        if (course.code && course.name) {
          // Format the course data to match the screenshot format
          const formattedCode = course.code.toString().trim();
          let formattedName = course.name.toString().trim();
          const formattedSemester = course.semester ? course.semester.toString().trim() : '';
          const section = course.section ? course.section.toString().trim() : '';
          
          console.log(`Processing course ${index+1}:`, { 
            code: formattedCode, 
            name: formattedName, 
            semester: formattedSemester,
            section: section
          });
          
          // Add as a new course
          // If section exists, ensure it's part of the name for filtering
          const nameWithSection = section ? `${formattedName} - ${section}` : formattedName;
          console.log(`Adding course: ${formattedCode} - ${nameWithSection} (${formattedSemester})`);
          
          this.coursesOffered.push({
            code: formattedCode,
            name: nameWithSection,
            semester: formattedSemester,
            section: section
          });
          
          importedCourses.push({
            code: formattedCode,
            name: nameWithSection,
            semester: formattedSemester,
            section: section
          });
        } else {
          console.warn(`Skipping course at index ${index} due to missing code or name:`, course);
        }
      });
      
      // Save to localStorage for persistence
      this.saveCoursesOfferedToStorage();
      
      console.log(`Import complete: ${importedCourses.length} courses imported`);
      return { newCourses: importedCourses.length, updatedCourses: 0 };
    },
    saveCoursesOfferedToStorage() {
      try {
        localStorage.setItem('coursesOffered', JSON.stringify(this.coursesOffered));
        console.log('Saved coursesOffered to localStorage:', this.coursesOffered);
      } catch (error) {
        console.error('Error saving coursesOffered to localStorage:', error);
      }
    },
    loadCoursesOfferedFromStorage() {
      try {
        const savedCourses = localStorage.getItem('coursesOffered');
        if (savedCourses) {
          const parsedCourses = JSON.parse(savedCourses);
          if (Array.isArray(parsedCourses) && parsedCourses.length > 0) {
            this.coursesOffered = parsedCourses;
            console.log(`Loaded ${parsedCourses.length} courses from localStorage:`, parsedCourses);
          } else {
            console.log('No courses found in localStorage or invalid format');
            this.coursesOffered = [];
          }
        } else {
          console.log('No saved courses found in localStorage');
          this.coursesOffered = [];
        }
      } catch (error) {
        console.error('Error loading coursesOffered from localStorage:', error);
        this.coursesOffered = [];
      }
    },
    toggleScheduleType(type) {
      const index = this.scheduleTypes.indexOf(type);
      if (index === -1) {
        this.scheduleTypes.push(type);
      } else {
        this.scheduleTypes.splice(index, 1);
      }
    },
    clearAllSchedules() {
      try {
        // Confirm before clearing
        if (!confirm('Are you sure you want to clear ALL schedules? This cannot be undone.')) {
          return;
        }
        
        // Clear all schedule-related data from localStorage
        localStorage.removeItem('labSchedules');
        localStorage.removeItem('sysadmin_schedules');
        localStorage.removeItem('acad_coor_schedules');
        localStorage.removeItem('schedules');
        localStorage.removeItem('viewer_schedules');
        localStorage.removeItem('generic_schedules');
        
        // Reset the component's schedule arrays
        this.allSchedules = [];
        this.schedules = [];
        
        console.log('All schedules cleared');
        alert('All schedules have been cleared successfully');
        
        // Reload the page to ensure everything is reset
        window.location.reload();
      } catch (error) {
        console.error('Error clearing schedules:', error);
        alert('Error clearing schedules. Please try again.');
      }
    },
    openEditDeleteModal(dayName, timeSlot) {
      const schedule = this.schedules.find(s => s.day === dayName && s.startTime === timeSlot && s.labRoom === this.selectedLab);
      if (schedule) {
        this.selectedSchedule = { ...schedule };
        
        // Parse times
        const startTimeParts = schedule.startTime.match(/(\d+):(\d+)\s+(AM|PM)/);
        const endTimeParts = schedule.endTime.match(/(\d+):(\d+)\s+(AM|PM)/);
        
        if (startTimeParts && endTimeParts) {
          this.editSchedule = {
            id: schedule.id,
            types: [...schedule.types],
            semester: schedule.semester,
            section: schedule.section,
            courseCode: schedule.courseCode,
            day: schedule.day,
            labRoom: schedule.labRoom,
            instructorName: schedule.instructorName,
            startHour: startTimeParts[1],
            startMinute: startTimeParts[2],
            startPeriod: startTimeParts[3],
            endHour: endTimeParts[1],
            endMinute: endTimeParts[2],
            endPeriod: endTimeParts[3],
            secondDay: schedule.secondDay
          };
          
          this.showEditDeleteModal = true;
        }
      }
    },
    
    openEditSchedule() {
      this.showEditDeleteModal = false;
      
      // Pre-fill the edit form with current values
      this.editSchedule = {
        id: this.selectedSchedule.id,
        types: [...this.selectedSchedule.types],
        semester: this.selectedSchedule.semester,
        section: this.selectedSchedule.section,
        courseCode: this.selectedSchedule.courseCode,
        day: this.selectedSchedule.day,
        labRoom: this.selectedSchedule.labRoom,
        instructorName: this.selectedSchedule.instructorName,
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: this.selectedSchedule.secondDay
      };
      
      setTimeout(() => {
        this.showEditScheduleModal = true;
      }, 100);
    },
    
    toggleEditScheduleType(type) {
      const index = this.editSchedule.types.indexOf(type);
      if (index === -1) {
        this.editSchedule.types.push(type);
      } else {
        this.editSchedule.types.splice(index, 1);
      }
    },
    
    updateSchedule() {
      // Validate fields
      if (!this.editSchedule.semester || !this.editSchedule.day || !this.editSchedule.labRoom || !this.editSchedule.courseCode) {
        alert('Please fill in all required fields');
        return;
      }
      
      if (!this.editSchedule.startHour || !this.editSchedule.endHour) {
        alert('Please select start and end times');
        return;
      }
      
      // Format time strings
      const startTime = `${this.editSchedule.startHour}:${this.editSchedule.startMinute} ${this.editSchedule.startPeriod}`;
      const endTime = `${this.editSchedule.endHour}:${this.editSchedule.endMinute} ${this.editSchedule.endPeriod}`;
      
      // Convert to minutes for validation
      const startMinutes = this.convertTimeToMinutes(startTime);
      const endMinutes = this.convertTimeToMinutes(endTime);
      const minStartTime = this.convertTimeToMinutes('7:30 AM');
      const maxEndTime = this.convertTimeToMinutes('8:00 PM');
      
      if (startMinutes < minStartTime) {
        alert('Schedule cannot start before 7:30 AM');
        return;
      }
      
      if (endMinutes > maxEndTime) {
        alert('Schedule cannot end after 8:00 PM');
        return;
      }
      
      if (endMinutes <= startMinutes) {
        alert('End time must be after start time');
        return;
      }

      // Check for overlapping schedules in the SAME SEMESTER, DAY, AND LAB ROOM, excluding the current schedule being edited
      const existingSchedules = this.allSchedules.filter(schedule => 
        schedule.semester === this.editSchedule.semester &&
        schedule.day === this.editSchedule.day && 
        schedule.labRoom === this.editSchedule.labRoom &&
        schedule.id !== this.selectedSchedule.id && // Exclude the current schedule being edited
        !schedule.isDeleted
      );

      console.log('All existing schedules in this SEMESTER/LAB/DAY for edit:', existingSchedules);
      console.log('Checking for conflicts with updated schedule in semester:', this.editSchedule.semester);

      // ======= IMPROVED OVERLAP DETECTION LOGIC =========
      let hasOverlap = false;
      for (const schedule of existingSchedules) {
        // Convert string times to minutes for precise comparison
        const existingStartMinutes = this.convertTimeToMinutes(schedule.startTime);
        const existingEndMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        console.log('Checking potential overlap for edit between:');
        console.log(`- New schedule: ${startTime} to ${endTime} (${startMinutes} to ${endMinutes} minutes)`);
        console.log(`- Existing: ${schedule.startTime} to ${schedule.endTime} (${existingStartMinutes} to ${existingEndMinutes} minutes)`);
        
        // Case 1: New schedule starts during existing schedule
        // (newStart >= existingStart && newStart < existingEnd)
        const newStartsDuringExisting = 
          startMinutes >= existingStartMinutes && 
          startMinutes < existingEndMinutes;
        
        // Case 2: New schedule ends during existing schedule
        // (newEnd > existingStart && newEnd <= existingEnd)
        const newEndsDuringExisting = 
          endMinutes > existingStartMinutes && 
          endMinutes <= existingEndMinutes;
        
        // Case 3: New schedule completely contains existing schedule
        // (newStart <= existingStart && newEnd >= existingEnd)
        const newContainsExisting = 
          startMinutes <= existingStartMinutes && 
          endMinutes >= existingEndMinutes;
        
        // No overlap only when:
        // 1. New schedule ends at or before existing schedule starts
        // 2. OR New schedule starts at or after existing schedule ends
        const noOverlap = 
          endMinutes <= existingStartMinutes || 
          startMinutes >= existingEndMinutes;
        
        // For debugging
        const overlapResult = {
          newStartsDuringExisting,
          newEndsDuringExisting,
          newContainsExisting,
          noOverlap,
          hasOverlap: !noOverlap
        };
        
        console.log('Overlap check results for edit:', overlapResult);
        
        if (!noOverlap) {
          hasOverlap = true;
          break;
        }
      }

      if (hasOverlap) {
        alert(`Cannot update schedule to this time slot. There is already a schedule for ${this.editSchedule.day} in ${this.editSchedule.labRoom} that overlaps with ${startTime} - ${endTime}.`);
        return;
      }
      
      // Find course name
      const selectedCourse = this.availableCoursesOffered.find(course => course.code === this.editSchedule.courseCode);
      const courseName = selectedCourse ? selectedCourse.name : '';
      
      // Calculate duration in minutes
      const durationMinutes = this.calculateDurationMinutes(startTime, endTime);
      
      // Create updated schedule object
      const updatedSchedule = {
        ...this.selectedSchedule,
        title: `${this.editSchedule.courseCode} (${this.editSchedule.types.length > 0 ? this.editSchedule.types.join('/') : this.selectedSchedule.types.join('/')})`,
        details: `${courseName}\n${this.editSchedule.section || this.selectedSchedule.section}\n${this.editSchedule.instructorName || this.selectedSchedule.instructorName}`,
        semester: this.editSchedule.semester || this.selectedSchedule.semester,
        section: this.editSchedule.section || this.selectedSchedule.section,
        courseCode: this.editSchedule.courseCode || this.selectedSchedule.courseCode,
        courseName: courseName,
        day: this.editSchedule.day || this.selectedSchedule.day,
        labRoom: this.editSchedule.labRoom || this.selectedSchedule.labRoom,
        instructorName: this.editSchedule.instructorName || this.selectedSchedule.instructorName,
        startTime: startTime,
        endTime: endTime,
        duration: durationMinutes,
        types: this.editSchedule.types.length > 0 ? [...this.editSchedule.types] : [...this.selectedSchedule.types],
        color: '#DD385A',
        status: 'draft', // Keep as draft after editing
        secondDay: this.editSchedule.secondDay
      };
      
      // Check for overlap on the second day if it's selected and different from the first day
      if (this.editSchedule.secondDay && this.editSchedule.secondDay !== this.editSchedule.day) {
        const secondDaySchedules = this.allSchedules.filter(schedule => 
          schedule.semester === this.editSchedule.semester &&
          schedule.day === this.editSchedule.secondDay && 
          schedule.labRoom === this.editSchedule.labRoom &&
          schedule.id !== this.selectedSchedule.id &&
          !schedule.isDeleted
        );
        
        console.log('All existing schedules for second day in edit mode:', secondDaySchedules);
        
        // Check for overlap on second day
        hasOverlap = false;
        for (const schedule of secondDaySchedules) {
          const existingStartMinutes = this.convertTimeToMinutes(schedule.startTime);
          const existingEndMinutes = this.convertTimeToMinutes(schedule.endTime);
          
          // Check for overlap using the same logic as for the main day
          const noOverlap = 
            endMinutes <= existingStartMinutes || 
            startMinutes >= existingEndMinutes;
          
          if (!noOverlap) {
            hasOverlap = true;
            break;
          }
        }
        
        if (hasOverlap) {
          alert(`Cannot update schedule at this time slot. There is already a schedule for ${this.editSchedule.secondDay} in ${this.editSchedule.labRoom} that overlaps with ${startTime} - ${endTime}.`);
          return;
        }
      }
      
      // Update the schedule in allSchedules
      const scheduleIndex = this.allSchedules.findIndex(s => s.id === this.selectedSchedule.id);
      if (scheduleIndex !== -1) {
        this.allSchedules[scheduleIndex] = updatedSchedule;
      }
      
      // Handle the secondary day scheduling
      // First, check if there was a previous second day schedule
      const previousSecondDayId = this.selectedSchedule.id + '-second';
      const previousSecondDayIndex = this.allSchedules.findIndex(s => s.id === previousSecondDayId);
      
      // Remove the previous second day schedule if it exists
      if (previousSecondDayIndex !== -1) {
        this.allSchedules.splice(previousSecondDayIndex, 1);
      }
      
      // Add a new second day schedule if necessary
      if (this.editSchedule.secondDay && this.editSchedule.secondDay !== this.editSchedule.day) {
        const secondDaySchedule = {
          ...updatedSchedule,
          id: updatedSchedule.id + '-second',
          day: this.editSchedule.secondDay
        };
        this.allSchedules.push(secondDaySchedule);
      }
      
      // Save changes to storage
      this.saveSchedulesToStorage();
      
      // Show success feedback
      alert('Schedule updated successfully');
      
      this.showEditScheduleModal = false;
      this.resetEditScheduleForm();
    },
    
    confirmDelete() {
      this.showEditDeleteModal = false;
      setTimeout(() => {
        this.showDeleteConfirmModal = true;
      }, 100);
    },
    
    deleteSchedule() {
      const scheduleId = this.selectedSchedule.id;
      const courseCode = this.selectedSchedule.courseCode;
      
      // Only allow deletion of draft schedules
      if (this.selectedSchedule.status !== 'draft') {
        alert('Only draft schedules can be deleted. This schedule is already ' + this.selectedSchedule.status);
        return;
      }
      
      try {
        // Remove from allSchedules array - both the main schedule and any second day schedule
        const secondDayId = scheduleId + '-second';
        this.allSchedules = this.allSchedules.filter(schedule => 
          schedule.id !== scheduleId && schedule.id !== secondDayId
        );
        
        // Get and update acad_coor_schedules in localStorage
        let existingSchedules = JSON.parse(localStorage.getItem('acad_coor_schedules') || '[]');
        
        // Handle both array and object with schedules property
        if (existingSchedules.schedules) {
          existingSchedules = existingSchedules.schedules;
        }
        
        // Make sure existingSchedules is an array
        if (!Array.isArray(existingSchedules)) {
          existingSchedules = [];
        }
        
        // Filter out the deleted schedule and its second day schedule if it exists
        const updatedSchedules = existingSchedules.filter(schedule => 
          schedule.id !== scheduleId && schedule.id !== secondDayId
        );
        
        // Save back to localStorage
        localStorage.setItem('acad_coor_schedules', JSON.stringify(updatedSchedules));
        
        // Update the filtered schedules display
        this.schedules = this.schedules.filter(schedule => 
          schedule.id !== scheduleId && schedule.id !== secondDayId
        );
        
        // Show success feedback
        alert(`Schedule deleted successfully! The course "${courseCode}" is now available for scheduling again.`);
        
        // Close modals and reset selected schedule
        this.showDeleteConfirmModal = false;
        this.selectedSchedule = null;
        
        // Refresh the schedules display
        this.filterSchedulesBySemester();
      } catch (error) {
        console.error('Error deleting schedule:', error);
        alert('Error deleting schedule. Please try again.');
      }
    },
    
    resetEditScheduleForm() {
      this.editSchedule = {
        id: null,
        types: [],
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: ''
      };
    },
    showImportCoursesModal() {
      this.showFileUploadModal = true;
    },
    clearCoursesOffered() {
      if (confirm('Are you sure you want to clear all course offerings? This cannot be undone.')) {
        console.log('Clearing coursesOffered from localStorage');
        localStorage.removeItem('coursesOffered');
        this.coursesOffered = [];
        alert('Course offerings have been cleared successfully.');
      }
    },
    filterSchedulesBySemester() {
      console.log('Filtering by semester:', this.selectedSemester);
      
      if (!this.selectedSemester || !this.allSchedules) {
        this.schedules = [];
        return;
      }
      
      // Show all schedules (draft, pending, and approved) in Schedule Management view
      this.schedules = this.allSchedules.filter(schedule => 
        schedule.semester === this.selectedSemester &&
        (schedule.status === 'draft' || schedule.status === 'pending' || schedule.status === 'approved')
      );
      
      console.log(`Filtered ${this.schedules.length} schedules for semester ${this.selectedSemester}`);
    },
    getScheduleStatus(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.day === dayName && 
        s.startTime === timeSlot && 
        s.labRoom === this.selectedLab
      );
      return schedule ? schedule.status : null;
    },
    sendForApproval(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.day === dayName && 
        s.startTime === timeSlot && 
        s.labRoom === this.selectedLab
      );

      if (schedule) {
        if (schedule.status !== 'draft') {
          alert('Only draft schedules can be sent for approval');
          return;
        }

        schedule.status = 'pending';
        this.saveSchedulesToStorage();
        alert('Schedule sent for approval successfully!');
      }
    },
    sendAllForApproval() {
      // Get all draft schedules for the current semester across ALL labs
      const draftSchedules = this.allSchedules.filter(schedule => 
        schedule.status === 'draft' &&
        schedule.semester === this.selectedSemester
        // No labRoom filter here, to include all labs
      );

      if (draftSchedules.length === 0) {
        alert('No draft schedules to send for approval for the selected semester');
        return;
      }

      try {
        // Get existing schedules from sysadmin_schedules
        let sysAdminSchedules = JSON.parse(localStorage.getItem('sysadmin_schedules') || '[]');
        if (sysAdminSchedules.schedules) {
          sysAdminSchedules = sysAdminSchedules.schedules;
        }
        if (!Array.isArray(sysAdminSchedules)) {
          sysAdminSchedules = [];
        }

        // Update status to pending for all draft schedules
        this.allSchedules = this.allSchedules.map(schedule => {
          if (draftSchedules.some(draft => draft.id === schedule.id)) {
            return { ...schedule, status: 'pending' };
          }
          return schedule;
        });

        // Add pending schedules to sysadmin_schedules without duplicates
        const pendingSchedules = this.allSchedules.filter(s => s.status === 'pending');
        pendingSchedules.forEach(pendingSchedule => {
          const exists = sysAdminSchedules.some(s => s.id === pendingSchedule.id);
          if (!exists) {
            sysAdminSchedules.push(pendingSchedule);
          }
        });

        // Save to both storages to maintain visibility in both views
        localStorage.setItem('sysadmin_schedules', JSON.stringify(sysAdminSchedules));
        localStorage.setItem('acad_coor_schedules', JSON.stringify(this.allSchedules));
        
        // Refresh the schedules display
        this.filterSchedulesBySemester();
        
        alert(`All schedules for ${this.selectedSemester} have been sent for approval`);
      } catch (error) {
        console.error('Error sending schedules for approval:', error);
        alert('Error sending schedules for approval. Please try again.');
      }
    },
    validateStartTime() {
      const startTime = `${this.newSchedule.startHour}:${this.newSchedule.startMinute} ${this.newSchedule.startPeriod}`;
      const startMinutes = this.convertTimeToMinutes(startTime);
      const minStartTime = this.convertTimeToMinutes('7:30 AM');
      
      if (startMinutes < minStartTime) {
        alert('Schedule cannot start before 7:30 AM');
        // Reset to 7:30 AM
        this.newSchedule.startHour = '7';
        this.newSchedule.startMinute = '30';
        this.newSchedule.startPeriod = 'AM';
      }
    },
    
    validateEndTime() {
      const endTime = `${this.newSchedule.endHour}:${this.newSchedule.endMinute} ${this.newSchedule.endPeriod}`;
      const endMinutes = this.convertTimeToMinutes(endTime);
      const maxEndTime = this.convertTimeToMinutes('8:00 PM');
      
      if (endMinutes > maxEndTime) {
        alert('Schedule cannot end after 8:00 PM');
        // Reset to 8:00 PM
        this.newSchedule.endHour = '8';
        this.newSchedule.endMinute = '00';
        this.newSchedule.endPeriod = 'PM';
      }
    },
    handleInstructorSelect() {
      if (this.newSchedule.instructorName === 'add_new') {
        this.showAddInstructorModal = true;
        // Reset the selected value so dropdown still works if they cancel
        this.newSchedule.instructorName = '';
      }
    },
    addNewInstructor() {
      if (this.newInstructorName.trim()) {
        const newInstructor = this.newInstructorName.trim();
        
        // Add to instructors array
        this.instructors.push(newInstructor);
        
        // Sort instructors alphabetically
        this.instructors.sort();
        
        // Save to localStorage
        localStorage.setItem('instructors', JSON.stringify(this.instructors));
        
        // Set the new instructor as selected based on which form is open
        if (this.showCreateScheduleModal) {
          this.newSchedule.instructorName = newInstructor;
        } else if (this.showEditScheduleModal) {
          this.editSchedule.instructorName = newInstructor;
        }
        
        // Close modal and reset
        this.showAddInstructorModal = false;
        this.newInstructorName = '';
      }
    },
    loadInstructorsFromStorage() {
      try {
        const savedInstructors = localStorage.getItem('instructors');
        if (savedInstructors) {
          const parsedInstructors = JSON.parse(savedInstructors);
          if (Array.isArray(parsedInstructors) && parsedInstructors.length > 0) {
            this.instructors = parsedInstructors;
            console.log(`Loaded ${parsedInstructors.length} instructors from localStorage`);
          }
        }
      } catch (error) {
        console.error('Error loading instructors from localStorage:', error);
      }
    },
    handleEditInstructorSelect() {
      if (this.editSchedule.instructorName === 'add_new') {
        this.showAddInstructorModal = true;
        // Reset the selected value so dropdown still works if they cancel
        this.editSchedule.instructorName = '';
      }
    }
  },
  computed: {
    isFormValid() {
      return this.newSemester.semester && this.newSemester.schoolYear;
    },
    isScheduleFormValid() {
      return this.scheduleTypes.length > 0 &&
        this.newSchedule.semester &&
        this.newSchedule.section &&
        this.newSchedule.courseCode &&
        this.newSchedule.day &&
        this.newSchedule.labRoom &&
        this.newSchedule.instructorName &&
        this.newSchedule.startHour &&
        this.newSchedule.endHour;
    },
    isEditScheduleFormValid() {
      // Allow partial updates - no need to validate all fields
      // Just check if at least one field has been modified
      return true; // We'll validate specific fields in the updateSchedule method instead
    },
    // Filter out courses that are already in use in any schedule
    availableCoursesOffered() {
      // Start with all courses
      let filteredCourses = [...this.coursesOffered];
      
      // First filter by the selected semester if one is selected in create schedule modal
      if (this.showCreateScheduleModal && this.newSchedule.semester) {
        // Extract the semester part properly based on the format
        let selectedSemester;
        if (this.newSchedule.semester.includes('Summer')) {
          // For Summer semesters, just use "Summer"
          selectedSemester = "Summer";
        } else {
          // For regular semesters (1st Sem, 2nd Sem), extract the semester part
          selectedSemester = this.newSchedule.semester.split(' ')[0] + ' ' + this.newSchedule.semester.split(' ')[1];
        }
        
        filteredCourses = filteredCourses.filter(course => 
          course.semester && course.semester.includes(selectedSemester)
        );
      }
      
      // Then filter by the selected section if one is selected in create schedule modal
      if (this.showCreateScheduleModal && this.newSchedule.section) {
        filteredCourses = filteredCourses.filter(course => 
          course.name && course.name.includes(this.newSchedule.section)
        );
      }
      
      if (!this.schedules || this.schedules.length === 0) {
        return filteredCourses;
      }

      // If we're in edit mode, we need to include the course being edited
      const excludedCourseId = this.showEditScheduleModal && this.selectedSchedule ? 
                              this.selectedSchedule.id : null;
      
      // Create a list of used course code and section combinations
      const usedCombinations = this.schedules
        .filter(schedule => schedule.id !== excludedCourseId)
        .map(schedule => ({
          code: schedule.courseCode, 
          section: schedule.section
        }));
      
      // Filter out courses that are already used for the SAME SECTION
      return filteredCourses.filter(course => {
        // If we're in edit mode and this is the current course being edited, keep it
        if (this.showEditScheduleModal && 
            this.selectedSchedule && 
            course.code === this.selectedSchedule.courseCode) {
          return true;
        }
        
        // Get the current section we're trying to create a schedule for
        const currentSection = this.showCreateScheduleModal ? this.newSchedule.section : 
                              (this.showEditScheduleModal ? this.editSchedule.section : '');
        
        // Check if this exact course+section combination is already used
        const isCombinationUsed = usedCombinations.some(used => 
          used.code === course.code && used.section === currentSection
        );
        
        // Keep the course if it's not already used for this section
        return !isCombinationUsed;
      });
    }
  },
  mounted() {
    console.log('Schedule Management component mounted');
    
    // Load courses from localStorage instead of clearing them
    this.loadCoursesOfferedFromStorage();
    console.log(`Loaded ${this.coursesOffered.length} courses for the dropdown menu`);
    
    // Load instructors from localStorage
    this.loadInstructorsFromStorage();
    
    // Then load schedules and generate week days
    this.loadSchedulesFromStorage();
    this.generateWeekDays();
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 24px;
  color: #e91e63;
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.import-excel-wrapper {
  position: relative;
}

.import-excel-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.import-excel-btn i {
  font-size: 12px;
}

.import-excel-btn:hover {
  background-color: #45a049;
}

.import-instructions {
  margin-bottom: 15px;
}

.import-requirements {
  margin-top: 5px;
  padding-left: 20px;
}

.selected-file {
  margin: 15px 0;
  padding: 10px;
  background-color: #f1f1f1;
  border-radius: 4px;
}

.import-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.import-btn:hover {
  background-color: #45a049;
}

.import-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.create-schedule-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 8px 16px;
  background-color: #e91e63;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.create-schedule-btn i {
  font-size: 12px;
}

.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.select-semester {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 200px;
}

.select-semester label {
  font-weight: 500;
  white-space: nowrap;
  color: #666;
}

.select-semester .select-wrapper {
  width: 180px;
}

.select-semester .form-select {
  border: 1px solid #ccc;
  font-size: 14px;
  padding: 6px 10px;
  height: 36px;
  width: 180px;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #DD385A;
}

.select-wrapper::after {
  display: none;
}

.lab-navigation {
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 0.5rem;
  border-bottom: 1px solid #DD385A;
  justify-content: space-between;
}

.nav-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  color: #DD385A;
}

.nav-icon {
  font-size: 1rem;
  font-style: normal;
}

.lab-indicator {
  background: none;
  color: #DD385A;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 0 0.5rem;
  min-width: 80px;
  text-align: center;
}

.week-header {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.time-header {
  width: 80px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px 10px;
}

.time-label {
  font-weight: 600;
  color: #e91e63;
  font-size: 0.9em;
}

.day-headers {
  display: flex;
  flex: 1;
}

.day-header {
  flex: 1;
  padding: 15px 10px;
  text-align: center;
  border-right: 1px solid #e0e0e0;
  background-color: #e91e63;
}

.day-name {
  font-weight: 600;
  color: #fff;
  font-size: 0.9em;
  margin-bottom: 4px;
}

.day-date {
  font-size: 0.8em;
  color: #fff;
}

.schedule-grid {
  display: flex;
  height: calc(100vh - 450px);
  overflow-y: auto;
  background-color: #fff;
  position: relative;
  max-height: calc((60px * 30) + 50px);
}

.time-column {
  width: 80px;
  border-right: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.schedule-content {
  display: flex;
  flex: 1;
  position: relative;
  min-height: calc(60px * 26);
}

.schedule-content::before {
  display: none;
}

.day-column {
  flex: 1;
  border-right: 1px solid #e0e0e0;
  position: relative;
  min-width: 120px;
  height: 100%;
  z-index: 2;
}

.day-column:last-child {
  border-right: none;
}

.day-slots {
  position: relative;
  height: 100%;
  min-height: calc(60px * 26);
}

.time-slot {
  height: 60px;
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

.time-column .time-slot {
  background-color: #fff;
  z-index: 2;
  padding-right: 10px;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  /* Remove the static background-color from here */
  padding: 8px;
  overflow: hidden;
  z-index: 10;
  color: white;
  box-shadow: none;
  border: none;
  box-sizing: border-box;
  transition: all 0.2s ease;
  cursor: pointer;
  margin: 0;
}

/* Add specific status-based color classes */
.schedule-item.status-draft {
  background-color: #DD385A; /* Red */
}

.schedule-item.status-pending {
  background-color: #FFA500; /* Orange/Yellow */
}

.schedule-item.status-approved {
  background-color: #4CAF50; /* Green */
}

.schedule-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
  transform: scale(1.005);
}

.schedule-content {
  width: 100%;
  height: 100%;
  cursor: pointer;
  user-select: none;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85em;
  margin-bottom: 4px;
  cursor: pointer;
}

.schedule-time {
  font-size: 0.75em;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  font-weight: 500;
  cursor: pointer;
}

.schedule-details {
  font-size: 0.75em;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  gap: 2px;
  white-space: pre-wrap;
  cursor: pointer;
}

.schedule-grid::-webkit-scrollbar {
  width: 8px;
}

.schedule-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.schedule-grid::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.schedule-grid::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.schedule-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: none;
  pointer-events: none;
  z-index: 1;
}

.time-slot::after {
  display: none;
}

.time-slot {
  border-bottom: 1px solid #e0e0e0;
}

.day-column .time-slot {
  position: relative;
  box-sizing: border-box;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  color: #DD385A;
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0;
}

.modal-body {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.schedule-type-selector {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 20px;
}

.type-btn {
  padding: 8px 24px;
  border: 1px solid #DD385A;
  background: white;
  color: #DD385A;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  min-width: 80px;
}

.type-btn:hover {
  background: #fff5f7;
}

.type-btn.active {
  background: #DD385A;
  color: white;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.modal-dropdown {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.modal-dropdown:focus {
  outline: none;
  border-color: #DD385A;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.cancel-btn, .create-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #ffebee;
  color: #DD385A;
  border: none;
}

.cancel-btn:hover {
  background: #ffdde3;
}

.create-btn {
  background: #DD385A;
  color: white;
  border: none;
  min-width: 120px;
}

.create-btn:hover {
  background: #c4314f;
}

.create-btn:disabled {
  background: #ddd;
  cursor: not-allowed;
}

.time-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.form-select:focus {
  border-color: #DD385A;
  outline: none;
}

.select-wrapper::after {
  display: none;
}

.time-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-select {
  width: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.period-select {
  width: 70px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.file-upload-area:hover {
  border-color: #DD385A;
  background-color: #fff5f7;
}

.upload-icon {
  width: 60px;
  height: 60px;
  background-color: #fff5f7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.upload-icon svg {
  color: #DD385A;
  width: 30px;
  height: 30px;
}

.file-format-text {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.sample-template {
  text-align: center;
  padding: 1rem 0;
  border-top: 1px solid #eee;
}

.download-sample-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #fff;
  color: #DD385A;
  border: 1px solid #DD385A;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.download-sample-btn:hover {
  background-color: #fff5f7;
}

.download-sample-btn i {
  font-size: 1rem;
}

.instructor-input {
  width: 100%;
  min-height: 60px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.instructor-input:focus {
  outline: none;
  border-color: #DD385A;
}

.schedule-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.send-for-approval-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-for-approval-btn:hover {
  background-color: #45a049;
}

.edit-btn, .delete-btn {
  padding: 0.85rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 180px;
  justify-content: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(to right, #DD385A, #e91e63);
  color: white;
  border: none;
}

.edit-btn:hover {
  background: linear-gradient(to right, #c4314f, #d81b60);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(221, 56, 90, 0.3);
}

.delete-btn {
  background: white;
  color: #DD385A;
  border: 2px solid #DD385A;
}

.delete-btn:hover {
  background: #fff5f7;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(221, 56, 90, 0.2);
}

.edit-btn i, .delete-btn i {
  font-size: 1.1rem;
}

.schedule-info {
  margin-top: 1rem;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f8f9fa;
}

.schedule-info p {
  margin: 0.75rem 0;
  font-size: 0.95rem;
  color: #333;
}

.schedule-info p strong {
  color: #DD385A;
  margin-right: 0.5rem;
}

.optional-text {
  color: #666;
  font-size: 0.8em;
  font-weight: normal;
  font-style: italic;
}

.form-select option[value=""] {
  font-style: italic;
  color: #666;
}

.import-note {
  margin-top: 5px;
  font-style: italic;
  color: #666;
  font-size: 0.9rem;
}

.center-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navigation-spacer {
  width: 200px;
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #ff9800;
  color: white;
  margin-right: 1rem;
}

.clear-btn:hover {
  background-color: #f57c00;
}

.clear-btn svg {
  margin-right: 4px;
}

.send-approval-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #2196F3;
  color: white;
  margin-right: 1rem;
}

.send-approval-btn:hover {
  background-color: #1976D2;
}

.send-approval-btn svg {
  margin-right: 4px;
}

.schedule-actions-footer {
  margin-top: 1rem;
  padding: 1rem;
  display: flex;
  justify-content: flex-end;
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.send-all-approval-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2);
}

.send-all-approval-btn:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.send-all-approval-btn i {
  font-size: 1rem;
}

.clear-courses-btn {
  background-color: #ff5722;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.clear-courses-btn i {
  font-size: 12px;
}

.clear-courses-btn:hover {
  background-color: #e64a19;
}

/* Add New Instructor Modal Styles */
.instructor-modal {
  max-width: 450px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.instructor-modal-header {
  background-color: #DD385A;
  color: white;
  padding: 15px 20px;
  border-bottom: none;
}

.instructor-modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.instructor-modal-body {
  padding: 25px;
  background-color: #f8f9fa;
}

.instructor-input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: all 0.3s;
  background-color: white;
}

.instructor-input:focus {
  border-color: #DD385A;
  box-shadow: 0 0 0 3px rgba(221, 56, 90, 0.2);
  outline: none;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 39px;
  color: #888;
}

.instructor-modal-footer {
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.instructor-cancel-btn {
  background-color: #f1f1f1;
  color: #555;
  border: none;
  padding: 10px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.instructor-cancel-btn:hover {
  background-color: #e1e1e1;
}

.instructor-add-btn {
  background-color: #DD385A;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.instructor-add-btn:hover {
  background-color: #c62e4e;
}

.instructor-add-btn:disabled {
  background-color: #f5a5b5;
  cursor: not-allowed;
}

.instructor-add-btn i {
  font-size: 14px;
}
</style>
