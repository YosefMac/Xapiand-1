/*
 * Copyright (c) 2005, Michael E. Smoot.
 * All rights reverved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#ifndef TCLAP_VALUESCONSTRAINT_H
#define TCLAP_VALUESCONSTRAINT_H

#include <string>
#include <vector>

#include "tclap/Constraint.h"

#if defined(HAVE_SSTREAM)
#include <sstream>
#elif defined(HAVE_STRSTREAM)
#include <strstream>
#else
#error "Need a stringstream (sstream or strstream) to compile!"
#endif

namespace TCLAP {

/**
 * A Constraint that constrains the Arg to only those values specified
 * in the constraint.
 */
template<class T>
class ValuesConstraint : public Constraint<T>
{

	public:

		/**
		 * Constructor.
		 * \param allowed - vector of allowed values.
		 */
		ValuesConstraint(std::vector<T>& allowed);

		/**
		 * Virtual destructor.
		 */
		virtual ~ValuesConstraint() {}

		/**
		 * Returns a description of the Constraint.
		 */
		virtual std::string description() const;

		/**
		 * Returns the short ID for the Constraint.
		 */
		virtual std::string shortID() const;

		/**
		 * The method used to verify that the value parsed from the command
		 * line meets the constraint.
		 * \param value - The value that will be checked.
		 */
		virtual bool check(const T& value) const;

	protected:

		/**
		 * The list of valid values.
		 */
		std::vector<T> _allowed;

		/**
		 * The string used to describe the allowed values of this constraint.
		 */
		std::string _typeDesc;

};

template<class T>
ValuesConstraint<T>::ValuesConstraint(std::vector<T>& allowed)
: _allowed(allowed),
  _typeDesc("")
{
    for ( unsigned int i = 0; i < _allowed.size(); i++ )
    {

#if defined(HAVE_SSTREAM)
        std::ostringstream os;
#elif defined(HAVE_STRSTREAM)
        std::ostrstream os;
#else
#error "Need a stringstream (sstream or strstream) to compile!"
#endif

        os << _allowed[i];

        std::string temp( os.str() );

        if ( i > 0 )
			_typeDesc += "|";
        _typeDesc += temp;
    }
}

template<class T>
bool ValuesConstraint<T>::check( const T& val ) const
{
	if ( std::find(_allowed.begin(),_allowed.end(),val) == _allowed.end() )
		return false;
	else
		return true;
}

template<class T>
std::string ValuesConstraint<T>::shortID() const
{
    return _typeDesc;
}

template<class T>
std::string ValuesConstraint<T>::description() const
{
    return _typeDesc;
}


} //namespace TCLAP
#endif

