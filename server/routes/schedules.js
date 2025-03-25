const express = require('express');
const router = express.Router();
const db = require('../config/db');
const authMiddleware = require('../middleware/auth');

// Get all semesters
router.get('/semesters', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM semesters ORDER BY name');
    res.json(rows);
  } catch (error) {
    console.error('Error fetching semesters:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get active semester
router.get('/semesters/active', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM semesters WHERE is_active = TRUE LIMIT 1');
    
    if (rows.length === 0) {
      return res.status(404).json({ message: 'No active semester found' });
    }
    
    res.json(rows[0]);
  } catch (error) {
    console.error('Error fetching active semester:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get all course offerings for a semester
router.get('/courses/:semesterId', async (req, res) => {
  try {
    const { semesterId } = req.params;
    
    const [rows] = await db.query(
      'SELECT * FROM course_offerings WHERE semester_id = ?',
      [semesterId]
    );
    
    res.json(rows);
  } catch (error) {
    console.error('Error fetching course offerings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Add course offerings
router.post('/courses', authMiddleware, async (req, res) => {
  try {
    const { courses, semesterId } = req.body;
    
    if (!Array.isArray(courses) || !semesterId) {
      return res.status(400).json({ message: 'Invalid request data' });
    }
    
    // Begin transaction
    await db.query('START TRANSACTION');
    
    // Insert each course
    for (const course of courses) {
      await db.query(
        'INSERT INTO course_offerings (code, name, semester_id) VALUES (?, ?, ?)',
        [course.code, course.name, semesterId]
      );
    }
    
    // Commit the transaction
    await db.query('COMMIT');
    
    res.status(201).json({ message: 'Courses added successfully' });
  } catch (error) {
    // Rollback in case of error
    await db.query('ROLLBACK');
    console.error('Error adding course offerings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get all lab rooms
router.get('/labs', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM lab_rooms ORDER BY name');
    res.json(rows);
  } catch (error) {
    console.error('Error fetching lab rooms:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get schedules filtered by semester and lab room
router.get('/', async (req, res) => {
  try {
    const { semester_id, lab_room_id } = req.query;
    
    let query = 'SELECT s.*, l.name as lab_room_name, sem.name as semester_name FROM schedules s ' +
                'JOIN lab_rooms l ON s.lab_room_id = l.id ' +
                'JOIN semesters sem ON s.semester_id = sem.id WHERE 1=1';
    
    const params = [];
    
    if (semester_id) {
      query += ' AND s.semester_id = ?';
      params.push(semester_id);
    }
    
    if (lab_room_id) {
      query += ' AND s.lab_room_id = ?';
      params.push(lab_room_id);
    }
    
    query += ' ORDER BY s.day, s.start_time';
    
    const [rows] = await db.query(query, params);
    res.json(rows);
  } catch (error) {
    console.error('Error fetching schedules:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create a new schedule
router.post('/', authMiddleware, async (req, res) => {
  try {
    const {
      title, details, semester, section, courseCode, courseName,
      day, labRoom, instructorName, startTime, endTime, duration, types
    } = req.body;
    
    // Get semester_id from name
    const [semesterRows] = await db.query(
      'SELECT id FROM semesters WHERE name = ?',
      [semester]
    );
    
    if (semesterRows.length === 0) {
      return res.status(404).json({ message: 'Semester not found' });
    }
    
    // Get lab_room_id from name
    const [labRoomRows] = await db.query(
      'SELECT id FROM lab_rooms WHERE name = ?',
      [labRoom]
    );
    
    if (labRoomRows.length === 0) {
      return res.status(404).json({ message: 'Lab room not found' });
    }
    
    const userId = req.user.id;
    const semesterId = semesterRows[0].id;
    const labRoomId = labRoomRows[0].id;
    
    // Insert schedule
    const [result] = await db.query(
      `INSERT INTO schedules 
      (title, details, semester_id, section, course_code, course_name, day, 
      lab_room_id, instructor_name, start_time, end_time, duration, schedule_types, created_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [title, details, semesterId, section, courseCode, courseName, day, 
       labRoomId, instructorName, startTime, endTime, duration, types.join('/'), userId]
    );
    
    res.status(201).json({ 
      id: result.insertId,
      message: 'Schedule created successfully' 
    });
  } catch (error) {
    console.error('Error creating schedule:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update a schedule
router.put('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const {
      title, details, semester, section, courseCode, courseName,
      day, labRoom, instructorName, startTime, endTime, duration, types
    } = req.body;
    
    // Get semester_id from name
    const [semesterRows] = await db.query(
      'SELECT id FROM semesters WHERE name = ?',
      [semester]
    );
    
    if (semesterRows.length === 0) {
      return res.status(404).json({ message: 'Semester not found' });
    }
    
    // Get lab_room_id from name
    const [labRoomRows] = await db.query(
      'SELECT id FROM lab_rooms WHERE name = ?',
      [labRoom]
    );
    
    if (labRoomRows.length === 0) {
      return res.status(404).json({ message: 'Lab room not found' });
    }
    
    const semesterId = semesterRows[0].id;
    const labRoomId = labRoomRows[0].id;
    
    // Update schedule
    await db.query(
      `UPDATE schedules SET
      title = ?, details = ?, semester_id = ?, section = ?, course_code = ?, 
      course_name = ?, day = ?, lab_room_id = ?, instructor_name = ?, 
      start_time = ?, end_time = ?, duration = ?, schedule_types = ?
      WHERE id = ?`,
      [title, details, semesterId, section, courseCode, courseName, day, 
       labRoomId, instructorName, startTime, endTime, duration, types.join('/'), id]
    );
    
    res.json({ message: 'Schedule updated successfully' });
  } catch (error) {
    console.error('Error updating schedule:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete a schedule
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    await db.query('DELETE FROM schedules WHERE id = ?', [id]);
    
    res.json({ message: 'Schedule deleted successfully' });
  } catch (error) {
    console.error('Error deleting schedule:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 