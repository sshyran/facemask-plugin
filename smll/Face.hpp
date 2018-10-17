/*
* Face Masks for SlOBS
* smll - streamlabs machine learning library
*
* Copyright (C) 2017 General Workings Inc
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
*/
#ifndef __SMLL_FACE_HPP__
#define __SMLL_FACE_HPP__

#include <stdexcept>

#pragma warning( push )
#pragma warning( disable: 4127 )
#pragma warning( disable: 4201 )
#pragma warning( disable: 4456 )
#pragma warning( disable: 4458 )
#pragma warning( disable: 4459 )
#pragma warning( disable: 4505 )
#pragma warning( disable: 4267 )
#pragma warning( disable: 4100 )
#include <dlib/image_processing.h>
#include <opencv2/opencv.hpp>
#include <opencv2/tracking.hpp>
#pragma warning( pop )

#include "landmarks.hpp"
#include "sarray.hpp"

namespace smll {

	class FaceDetector;

	class Face
	{
	public:
		Face();
		Face(const Face& f) { *this = f; }
		~Face();
		Face& operator=(const Face& f);

		dlib::rectangle				m_bounds;
		int							m_trackingX;
		int							m_trackingY;
		double						m_trackingScale;
		cv::Ptr<cv::Tracker> tracker;

		void StartTracking(const cv::Mat& image) {
			tracker->clear();
			cv::Rect2d bounds = cv::Rect2d(cv::Point2d(m_bounds.left(), m_bounds.top()),
										   cv::Point2d(m_bounds.right(), m_bounds.bottom()));
			tracker->init(image, bounds);
		}

		bool UpdateTracking(const cv::Mat& image) {
			cv::Rect2d bounds;
			bool trackingSuccess = tracker->update(image, bounds);
			m_bounds = dlib::rectangle(bounds.tl().x, bounds.tl().y, bounds.br().x, bounds.br().y);

			return trackingSuccess;
		}

		dlib::rectangle getBounds() {
			dlib::rectangle bounds;
			bounds.set_left((long)((m_bounds.left() + m_trackingX) * m_trackingScale));
			bounds.set_right((long)((m_bounds.right() + m_trackingX) * m_trackingScale));
			bounds.set_top((long)((m_bounds.top() + m_trackingY) * m_trackingScale));
			bounds.set_bottom((long)((m_bounds.bottom() + m_trackingY) * m_trackingScale));
			return bounds;
		}
	};

	// Just to keep memory clean, statically allocate faces
	const int		MAX_FACES = 8;
	typedef sarray<Face, MAX_FACES> Faces;

} // smll namespace
#endif // __SMLL_FACE_HPP__

